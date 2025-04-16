# Customized HPC Cluster Software Stack on QCT Developer Cloud

Stephen Chang Research and Development Department Quanta Cloud Technology Taoyuan City, Taiwan Stephen.Chang@QCT.io

*Abstract -* **OpenHPC is a collaborative project conducted by Linux Foundation to lower barriers to deployment, management, and use of modern HPC system with reference collection of open-source HPC software components and best practices. Quanta Cloud Technology (QCT) customized HPC cluster software stack including system provisioning, core HPC services, development tools, and optimized applications and libraries, which are distributed as pre-built and validated binaries and are meant to seamlessly layer on top of popular Linux distributions with the integration conventions defined by OpenHPC project. The architecture of QCT HPC Cluster Software Stack is intentionally modular to allow end users to pick and choose from the provided components, as well as to foster a community of open contribution. This paper presents an overview of the underlying customized vision, system architecture, software components and run tests on QCT Developer Cloud.**

#### *Keywords – HPC, OpenHPC, Software Stack, QCT Developer Cloud*

# I. INTRODUCTION

It is difficult and tedious for most of HPC sites without dedicated support team or skillful IT staffs to rapidly build and operate a capable HPC system by aggregating a large suite of open-source components for their users [1-3]. This is motivated by the necessity to build and deploy HPC focused packages that are either absent or outdated in popular Linux distributions. Further, combined with a desire to minimize duplication and share best practices across sites, the OpenHPC community project was formed. [4]

Launched initially in November 2015, and formalized as a collaborative Linux Foundation project in June 2016, OpenHPC is a collaborative, community effort that initiated from a desire to aggregate a number of common ingredients required to deploy and manage HPC Linux clusters and provides re-usable building blocks for the HPC community and plans to identify and develop abstraction interfaces between key components to further enhance modularity and interchangeability. The community includes representation from a variety of sources including software vendors,

Andy Pan Business Development Department Quanta Cloud Technology Taoyuan City, Taiwan Andy.Pan@QCT.io

equipment manufacturers, research institutions, supercomputing sites, and others. [5]

Refer to the reference architecture and integration conventions used in OpenHPC project, QCT customizes HPC Cluster software stack as a convenient tool, QCT HPC Cluster Enablement Kit for Linux (QCEK), based on customized and fine-tuned open-source software stack including system provisioning and administration tools, resource management and job scheduler, core networking and I/O services, development tools, and optimized applications and libraries. We use QCEK to rapidly implement a full-featured HPC Linux cluster system on our internal QCT Developer Cloud.

 With QCT HPC Cluster Enablement Kit for Linux with adaptive and powerful QCT hardware products, users can simplify the installation, management, and ongoing maintenance of an HPC system by reducing the amount of integration and validation effort required to accelerate their time to results and value for their HPC initiatives.

#### II. RELATED WORKS

As mentioned in the previous section, leverage with great open-source community efforts and software components to build up an easy-to-use and easy-to-manage HPC system can be easy and efficient. Before OpenHPC project launched, a variety of open-source tools and cluster management software to address this problem. Among those solutions, OSCAR, Rocks and xCAT are well-known.

OSCAR (Open Source Cluster Application Resources) [6] contains everything needed to users, regardless of their experience level with a *nix environment, to install a Beowulf type high performance computing cluster for immediate use. It also has a robust and extensible testing architecture and a rich set of pre-packages applications or utilities to let administrators create customized packages for any kind of distributed applications on top of a standard installation of a supported Linux distributions. However, the project is no longer actively maintained and the latest release under current status shown on its official website is OSCAR 6.0.3.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:43:38 UTC from IEEE Xplore. Restrictions apply.

This work is sponsored by Quanta Cloud Technology at San Jose, United States.

Rocks [7] is an open-source Linux cluster distribution that enables end users to easily build computational clusters, grid endpoints and visualization tiled-display walls. It was initially based on the Red Hat Linux distribution and recent versions of Rocks were based on CentOS, with a modified Anaconda installer that simplifies mass installation onto many computers. Installations can be customized with additional software packages at install-time by using special user-supplied CDs and extend the system by integrating seamlessly and automatically into the management and packaging mechanisms used by base software, greatly simplifying installation and configuration of large numbers of computers. The most recent version of Rocks, version 6.2 (Sidewinder), was released in May 2015 and is based on CentOS (v6.6).

xCAT [8], Extreme Cluster/Cloud Administration Toolkit, offers complete management of clouds, clusters, HPC, grids, datacenters, renderfarms, online gaming infrastructure, and whatever tomorrows next buzzword may be. It is open-source, agile, extensible, and based on years of system administration best practices and experience. It also has more installation options to provision OS on physical or virtual machines, remotely manage systems and quickly configure and control management node services. There are two core components - *xcat-core* and *xcat-dep* are needed to install xCAT for multiple operating systems and hardware platforms via different install options such as downloading the *tar.bz2* packages, accessing online repositories from target machine, or cloning source files to build. The latest official released version of xCAT is 2.13.3.

Compare OSCAR, Rocks and xCAT with their features and design, OSCAR and Rocks are simple to use but they can't meet essential prerequisites for modern HPC systems such as supported for the latest hardware and OS versions due to poor supports or discontinued development from their open-source communities. xCAT has the most complete features designed to take advantages of IBM and Lenovo hardware to build up HPC systems supported for multiple operating systems with the latest versions but maybe the openness is an issue for other hardware vendors.

Other proprietary and commercial solutions such as Bright Cluster Manager provide the all-in-one solution to mitigate the complexity of HPC implementation and management. It is great but not affordable for all users.

To make sure the openness and to get active participations from open-source community will be the key to build up a modern HPC cluster management system. It should be providing an HPC focused software repository and adopts a more building-block approach. It also is intended to offer a greater diversity, flexibility, compatibility and interoperability for system components. Furthermore, as a community effort, it should be supported and maintained by a group of vendors, research centers and laboratories that share common goals of minimizing duplicated effort and sharing of best practices.

Now OpenHPC community seeks to leverage standard Linux tools and practices to install and maintain software distribution and allow users to further extend and customize their environment. With similar goals, we aim to provide a free and convenient HPC cluster enablement kit with a complete cluster software stack capable of provisioning and administering a system in addition to popular optimized applications for certified QCT hardware platform for building a HPC cluster system in the most simplified manner.

## III. SYSTEM DESIGN AND COMPONENTS

## A. *System Architecture*

![](_page_1_Figure_9.png)

The recommended system architecture – Figure 1 used for any HPC Cluster has several networks:

1) *In-Band internal management Ethernet network.* 

The In-Band management network is attached to all nodes in a system and available to each node's host operating system. The purpose of this network is to provide remote access from the system's login nodes and communication between HPC cluster system daemons.

2) *Out-ot-Band (OOB) power control and console Ethernet network.* 

The OOB network is attached to all nodes in the system, but only available to the host operating system on the system's admin / head nodes. The connection is used to communicate with BMC within each node for node power control and console access. If Smart PDUs are being used for power control the Smart PDUs are connected into the system via the OOB network.

3) *High-performance low-latency network or fabric, e.g. Mellanox InfiniBand or Intel Omni-Path for MPI and network file service.* 

The high-performance low-latency network or fabric is attached to each computing node in the system for intra-job communication, usually via MPI. If the fabric requires a Subnet Manager to be run on a node it is common for the system admin / head nodes to also be attached to the fabric and run the fabric management daemons.

4) *A shared or optional dedicated network for parallel file system service* 

In any HPC cluster, a NFS-based shared or high performance parallel file system such as Lustre [9] provides all nodes to access shared file system. A system's highperformance low-latency fabric is often used to access a Lustre file system. The fabric is either directly attached to the Lustre file system or to Lustre router nodes, which are attached to a Storage Area Network (SAN) over which the Lustre file system is available.

 It is highly recommended that the perimeter of the system (any node within an QCT HPC Cluster with external access) be protected by a firewall.

## B. *Software Components*

![](_page_2_Figure_3.png)

Figure 2 – Necessary Software Components

There are a lot of system software components – Figure 2 to be used in a modern HPC system: (1) Hardware based management software, which is software tools used for specific hardware supports or management tools such as firmware updater and IPMI management tools; (2) Base operating systems like Red Hat Enterprise Linux, CentOS and Scientific Linux operating system or specific device drivers such as GPU, NIC, HBA or OPA/InfiniBand OFED drivers; (3) Run-time libraries and language tools, which includes C/C++/Fortran/Perl/Python compilers or run-time libraries such as GLIBC and math libraries; (4) Provisioning tools and configuration management system for deploying OS and managing applications packages and their configurations; (5) Monitoring and reporting tools, which include system-wide In-band or Out-of-Band real-time system monitoring, event management and reporting tools; (6) Resource / workload manager and job scheduler that is integrated resource and workload management system such as PBS Pro / SLURM or dedicated resource manager and job scheduler such as Torque and Maui / Moab; (7) Application frameworks for specific applications such as NVIDIA CUDA, MPI (OpenMPI, MVAPICH2, Intel MPI) or Deep Learning Frameworks (Caffe, TensorFlow or Theano); (8) Optimized user-spaced applications or industrial / vertical applications such as WRF, Quantum Espresso, VASP, or ANSYS Fluent.

#### C. *HPC Cluster Software Stack*

 QCT HPC Linux Cluster Software Stack includes four major layers, which are adaptive platform layer, operating system layer, system management layer and service layer. The adaptive platform indicates the hardware platform for HPC infrastructure such as servers, networking and storage. The operating system is mainly Linux-based Operating systems with shared NFS-based or parallel file system. The system management layer includes system deployment, system monitoring and system operations. The service layer includes inbound and outbound networking; resource and workload management, MPI environment, compilers with Math libraries and application frameworks.

![](_page_2_Figure_9.png)

![](_page_2_Figure_10.png)

QCT adopts Cobbler with system-wide DHCP and PXE services and Ansible as the system deployment tool and configuration management system, respectively. For system monitoring tools, Pacemaker and Colosync can be used for enabling high-availability features for specific and important services. Ganglia and Nagios provide the real-time webbased monitoring and flexible event management, respectively. QCT also integrates Collectl, a script-based tool for collecting performance metrics for system and Lustre, and Quanta System Manager (QSM) [10], which is a webbased GUI for power management and system monitoring designed for out-of-band management system via BMC or serial networks by QCT. To help administrator and end-user efficiently manage or utilize the cluster, Parallel Distributed Shell (PDSH) [11], an efficient, multithreaded remote shell client which executes commands on multiple remote hosts in parallel, and Environment Modules package [12], which is a tool that simplify shell initialization and lets users easily modify their environment during the session with module files, are well-configured in the software stack. LVS package is used for load balanced service for incoming network traffic from external network to internal login nodes. Iptables is system-wide firewall service with the NAT feature for processing all outbound network traffic to Intranet or Internet. Resource and workload management is always the important component in HPC system. QCT support three major tools, Torque [13], PBS Pro [14] and Slurm [15]. Torque resource manager provides control over batch jobs and distributed computing resources. It can integrate with Maui [16], open-source job scheduler, or Moab [17], an optional workload manager with commercial supports. PBS Professional is industry-leading workload manager and job scheduler for HPC environments. PBS Professional Open Source Project is open-source with community supports. Slurm is an open source, fault-tolerant, and highly scalable cluster management and job scheduling system for large and small Linux clusters. Slurm requires no kernel modifications for its operation and is relatively self-contained.

The service layer is on the top of the software stack. It includes MPI environments, compilers and libraries, and application framework. Message Passing Interface (MPI) is a standardized and portable message-passing system designed by a group of researchers from academia and industry to function on a wide variety of parallel computing architectures. Popular MPI implementations include opensource OpenMPI [18], MPICH [19] and MVAPICH [20] and optional Intel MPI [21] with commercial supports. QCT also pre-configured the system-wide compilers and libraries such as GNU C/C++, GNU Fortran and others with optional Math libraries such as BLAS and LAPACK and ALTAS in any Linux distributions for the end-users. Intel [22] and PGI [23] C/C++/Fortran compilers, libraries and tools are most popular commercial products used in developing HPC applications. For GPU computing and AI, CUDA [24], a parallel computing platform and programming model invented by NVIDIA, and Caffe [25] and Tensorflow [26], which are very popular frameworks for deep learning applications, are both include in the QCT software stack. CUDA enables dramatic increases in computing performance by harnessing the power of the graphics processing unit (GPU).

## D. *QCT HPC Cluster Solution Kits*

## 1) *QCT HPC Cluster Enablement Kit for Linux*

It is an integrated and convenient tool to rapidly deploy the OS, optimized software components and applications by QCT. The enablement kit in QCT HPC/ML software stack is used only for certified QCT HPC hardware platform. It can help the administrator to easily and quickly install HPC core services and tools used to build up a complete HPC Linux cluster. The customized and fine-tuned MPI packages, CUDA and ML frameworks, and industrial open-source applications with best practices are also included in the enablement kit. The rest of the features and tools include the built-in performance benchmarking and test tools, integrated open-source system monitoring and management tools and QSM for IT administrators, pre-configured resource management system and job scheduler, NFS or optional Lustre file system ready, compliant with OpenHPC integration conventions and RHEL / CentOS / Scientific Linux 7.3 support.

#### 2) *QCT Deployment Kit for OpenHPC*

There are two versions of deployment kits for OpenHPC. One is an integrated tool with Intel HPC Orchestrator, the Intel supported version of the OpenHPC software stack, and value-add components by QCT to deploy OS and OpenHPC software stack for certified QCT HPC platform. The other is a tool with simplified process to deploy OS and official OpenHPC components for certified QCT HPC hardware products.

## IV. USE AND TEST ON QCT DEVELOPER CLOUD

To facilitate validation of the QCT HPC Cluster OpenHPC Enablement Kit, we first provision a cluster by using QCT HPC Cluster Enablement Kit from beta-metal on our QCT Developer Cloud – Figure 4.

Once the cluster is up and running, we launch a suite of tests targeting the functionality of each component. These tests aim to insure development toolchains are functioning correctly.

 Then, we run HPL, Iperf and IOR performance benchmarks to test for computing, networking and storage. Finally, we use different user accounts to access the HPC system and simultaneously execute different applications such WRF and Quantum Espresso via job submission to ensure jobs perform under the resource manager and the QCT HPC Cluster Software Stack is functionally integrated.

![](_page_3_Figure_10.png)

Figure 4 – HPC Cluster on QCT Developer Cloud

#### V. CONCLUSION AND FUTURE WORKS

This paper has presented an overview of QCT HPC Cluster tool kits with QCT HPC Cluster Software Stack, a customized and layered based collections of software components, used for rapidly build a HPC Cluster system and run tests on QCT Developer Cloud.

In the future, we will actively participate in OpenHPC community and work with professionals to focused on optimizing software components and user applications for OpenHPC. Currently, QCT HPC Cluster tool kits provide simple and basic configuration and management features for HPC clusters, but future efforts will focus on providing automation for more advanced configuration and tuning to address scalability, power management, and high availability concerns. We also hope to offer more contribution to the whole community.

## ACKNOWLEDGMENT

We would like to thank the Linux Foundation and associated members of the OpenHPC collaborative project for supporting this community effort. We are particularly grateful to the additional members of the research and development department including Paul Young, Roscoe Lin, Prabha Madhavan and Veda Shankar.

#### REFERENCES

- [1] Y.-C. Fang, Y. Gao, and C. Stap, "Future Enterprise Computing Looking into 2020," in *Frontier and Innovation in Future*
*Computing and Communications*, J. J. Park, A. Zomaya, H.-Y. Jeong, and M. Obaidat, Eds., ed Dordrecht: Springer Netherlands, 2014, pp. 127-134.

- [2] Y. Gao, S. Iqbal, P. Zhang, and M. Qiu, "Performance and Power Analysis of High-Density Multi-GPGPU Architectures: 6A Preliminary Case Study," presented at the Proceedings of the 2015 IEEE 17th International Conference on High Performance Computing and Communications, 2015 IEEE 7th International Symposium on Cyberspace Safety and Security, and 2015 IEEE 12th International Conf on Embedded Software and Systems, 2015.
- [3] Y. Gao and P. Zhang, "A Survey of Homogeneous and Heterogeneous System Architectures in High Performance Computing," in *2016 IEEE International Conference on Smart Cloud (SmartCloud)*, 2016, pp. 170-175.
- [4] "Cluster Computing with OpenHPC" presented at *Inaugural HPC Systems Professionals Workshop, Nov. 14, 2016.* Available: https://github.com/openhpc/ohpc/files/619162/HPCSYSPROS1

|  | http://openhpc.community/about-us/vision/ |  |  |  |
| --- | --- | --- | --- | --- |
| [5] | 6_OpenHPC.pdf2] OpenHPC | OpenHPC Vision/Misson. | Vision/Misson. | Available: Available: |

- http://openhpc.community/about-us/vision/
- [6] *OSCAR (Open Source Cluster Application Resources).* Available: http://svn.oscar.openclustergroup.org/
- [7] *ROCKS*. Available: http://www.rocksclusters.org/
- [8] *xCAT*. Available: https://xcat.org/
- [9] *Lustre*. Available: http://lustre.org
- [10] *QCT System Manager (QSM)*. Available: https://www.qct.io/product/index/software/Management_Tool/ Management_Tool/QSM
- [11] *Parallel Distributed Shell*. Available: https://sourceforge.net/projects/pdsh/
- [12] *Environment Modules*. Available: http://modules.sourceforge.net/
- [13] *Torque*. Available: http://www.adaptivecomputing.com/products/open-
- source/torque/ [14] *PBS Professional Open Source Project*. Available:
- http://www.pbspro.org/ [15] *SLURM Workload Manager*. Available: https://slurm.schedmd.com/
- [16] *Maui*. Available:
- http://www.adaptivecomputing.com/products/open-source/maui/ [17] *Moab HPC Suite*. Available: http://www.adaptivecomputing.com/products/hpc-
- products/moab-hpc-basic-edition/ [18] *Open MPI – Open Source High Performanc Computing*.
- Available: https://www.open-mpi.org/
- [19] *MPICH*. Available: http://www.mpich.org/ [20] *MVAPICH: MPI over InfiniBand, Omin-Path, Ethernet/iWARP,*
- *and RoCE*. Available: http://mvapich.cse.ohio-state.edu/ [21] *Intel MPI Library*. Available: https://software.intel.com/enus/intel-mpi-library/
- [22] *Intel Parallel Studio XE*. Available: https://software.intel.com/en-us/intel-parallel-studio-xe/
- [23] *PGI Compilers*. Available: http://www.pgroup.com/
- [24] *CUDA*. Available: https://developer.nvidia.com/cuda-zone/
- [25] *Caffe Deep Learning Framwork*. Available: http://caffe.berkeleyvision.org/
- [26] *TensorFlow An open-source software library for Machine Intelligence*. Available: https://www.tensorflow.org/

