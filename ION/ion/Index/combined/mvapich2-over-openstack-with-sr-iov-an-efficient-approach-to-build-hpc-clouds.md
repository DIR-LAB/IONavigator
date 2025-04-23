# MVAPICH2 over OpenStack with SR-IOV: An Efficient Approach to Build HPC Clouds

Jie Zhang, Xiaoyi Lu, Mark Arnold, Dhabaleswar K. (DK) Panda Department of Computer Science and Engineering

The Ohio State University

Email: {zhanjie, luxi, arnoldm, panda}@cse.ohio-state.edu

*Abstract*—Cloud Computing with Virtualization offers attractive flexibility and elasticity to deliver resources by providing a platform for consolidating complex IT resources in a scalable manner. However, efficiently running HPC applications on Cloud Computing systems is still full of challenges. One of the biggest hurdles in building efficient HPC clouds is the unsatisfactory performance offered by underlying virtualized environments, more specifically, virtualized I/O devices. Recently, Single Root I/O Virtualization (SR-IOV) technology has been steadily gaining momentum for high-performance interconnects such as Infini-Band and 10 GigE. Due to its near native performance for inter-node communication, many cloud systems such as Amazon EC2 have been using SR-IOV in their production environments. Nevertheless, recent studies have shown that the SR-IOV scheme lacks locality aware communication support, which leads to performance overheads for inter-VM communication within the same physical node.

In this paper, we propose an efficient approach to build HPC clouds based on MVAPICH2 over OpenStack with SR-IOV. We first propose an extension for OpenStack Nova system to enable the IVShmem channel in deployed virtual machines. We further present and discuss our high-performance design of virtual machine aware MVAPICH2 library over OpenStackbased HPC Clouds. Our design can fully take advantage of highperformance SR-IOV communication for inter-node communication as well as Inter-VM Shmem (IVShmem) for intra-node communication. A comprehensive performance evaluation with micro-benchmarks and HPC applications has been conducted on an experimental OpenStack-based HPC cloud and Amazon EC2. The evaluation results on the experimental HPC cloud show that our design and extension can deliver near bare-metal performance for implementing SR-IOV-based HPC clouds with virtualization. Further, compared with the performance on EC2, our experimental HPC cloud can exhibit up to 160X, 65X, 12X improvement potential in terms of point-to-point, collective and application for future HPC clouds.

*Keywords*—*Cloud Computing, OpenStack, SR-IOV, IVShmem, Virtualization, InfiniBand*

# I. INTRODUCTION

Cloud Computing with virtualization offers attractive capabilities to consolidate complex IT resources in a scalable manner by providing well-configured virtual machines. The desirable features of Cloud Computing for users such as ease of system management, configuration, and administration meet their various resource utilization requirements, including fast deployment, performance isolation, security, and live migration [25]. During the last decade, Cloud Computing with virtualization has gained momentum in HPC communities. For example, Amazon's Elastic Compute Cloud (EC2) [1] relies on virtualization to consolidate computing, storage and networking resources for various kinds of applications.

However, efficiently running HPC applications on Cloud Computing systems is still full of challenges. One of the biggest hurdles is the unsatisfactory performance offered by underlying virtualized environments, especially for the lower virtualized I/O performance [17]. More specifically, typical high performance MPI libraries such as MVAPICH2 [23] and OpenMPI [24], are able to provide sub-microsecond pointto-point latencies. However, recent studies [17] have shown that MPI performance in virtualization based Cloud Computing systems has been neglected. Such performance overheads of virtualization limit the adoption of Cloud Computing systems for HPC applications.

Recently, a new networking virtualization capability, Single Root I/O Virtualization (SR-IOV) [27] is emerging as an attractive feature for virtualizing I/O devices in Cloud Computing systems. SR-IOV can make a PCIe device present itself as multiple virtual devices and each virtual device can be dedicated to a single VM. By this novel feature, the performance gap between MPI point-to-point inter-node communication on virtual machines and physical machines can be significantly reduced [17]. Due to the high-performance nature, SR-IOV has been successfully used in production Cloud Computing systems, such as the C3, R3 and I2 instance types (using 10 GigE) in Amazon EC2 [1].

HPC applications benefit from SR-IOV by improving the inter-node communication performance on a virtualized cloud system. However, SR-IOV lacks locality aware communication support, which makes inter-VM communications within the same node use SR-IOV, leading to performance overheads. By contrast, high-performance communication libraries such as MPI in the HPC domain typically use shared memory based schemes for intra-node communication. In this context, another novel feature, inter-VM shared memory (IVShmem) [21], is proposed for improving inter-VM communication performance within one node. IVShmem supported applications on multiple VMs within a given host can effectively utilize shared memory backed communication, which can significantly improves the performance of intra-node inter-VM communication compared to SR-IOV on virtualized InfiniBand clusters [15], [16].

On the other hand, easy and scalable resource management offered by Cloud Computing systems with virtualization still motivates more and more users to move their applications to the cloud or building private clouds inside their own organizations. OpenStack [5] is one of the most popular opensource solutions to build a cloud and manage huge amounts

<sup>*</sup>This research is supported in part by National Science Foundation grants #OCI-1148371, #CCF-1213084, #CNS-1347189 and #CNS-1419123

of virtual machines. Taking into consideration the delivery of high performance HPC applications in the cloud, it is necessary to integrate and enable all the above features when building HPC clouds. Additionally, MPI libraries also need to be virtual machine aware and be able to fully take advantage of the provided novel features in clouds. All of these issues lead to the following broad challenges:

- 1) How to build an HPC Cloud with near native performance for MPI applications over SR-IOV enabled InfiniBand clusters?
- 2) How to design a high performance MPI library to efficiently take advantage of novel features such as SR-IOV and IVShmem provided in HPC clouds?
- 3) How much performance improvement can be achieved by our proposed design on MPI point-topoint operations, collective operations and applications in HPC clouds?
- 4) How much benefit the proposed approach with Infini-Band can provide compared to Amazon EC2?

To address these challenges, this paper proposes a new approach, based on MVAPICH2 over OpenStack with SR-IOV, to build HPC clouds with near native performance. We first propose an extension for the OpenStack Nova system to enable IVShmem in deployed virtual machines. We further present our high-performance design of the virtual machine aware MVAPICH2 library over OpenStack. Our design can fully take advantage of the high-performance SR-IOV communication channel for inter-node communication as well as the Inter-VM Shmem (IVShmem) channel for intra-node communication. A comprehensive performance evaluation with micro-benchmarks and HPC applications has been conducted on an experimental OpenStack-based HPC cloud. Through the performance comparison with Amazon EC2, which is a popular cloud computing platform with SR-IOV, we show that our design and extension can deliver near bare-metal performance for implementing SR-IOV-based HPC clouds with virtualization. In summary, this paper makes the following key contributions:

- 1) Extend OpenStack framework to support IVShmembased high-performance communication on HPC clouds
- 2) Design locality aware high performance MPI library on OpenStack-based clouds with SR-IOV enabled InfiniBand networks
- 3) Share early experiences of using the proposed approach, MVAPICH2 over OpenStack with SR-IOV, to build a local experimental HPC cloud efficiently
- 4) Conduct comprehensive performance evaluations to show that our proposed VM locality aware MVA-PICH2 library on extended OpenStack framework can reveal significant improvement potential for future HPC clouds. Compared with EC2, which is the best current generation cloud testbed, our experimental HPC cloud can deliver
- a) 160X improvement on intra-node point-topoint performance
- b) 65X improvement on intra-node collective performance
- c) 12X reduction on application execution time

To the best of our knowledge, this is the first paper that attempts to extend the OpenStack framework to not only ease system management, but also efficiently support high performance MPI communication over HPC clouds with SR-IOV enabled InfiniBand networks. This work will be extended further and installed on the NSF cloud testbed, Chameleon, which is a large-scale, reconfigurable experimental environment for next generation cloud research [2].

The rest of the paper is organized as follows. Section II provides an overview of OpenStack, SR-IOV, IVShmem, InfiniBand and Amazon EC2. Section III presents our experimental cloud deployment by OpenStack, extension to OpenStack to support IVShmem, and discusses virtual machine locality aware design alternatives. In Section IV, we present a case study of building a private HPC cloud. Based on this private HPC cloud, we conduct comprehensive performance evaluation in Section V. Finally, we introduce related work and make the conclusion.

# II. BACKGROUND

#### *A. OpenStack*

OpenStack [5] is a cloud operating system that controls large pools of compute, storage, and networking resources throughout a datacenter, all managed through a dashboard that gives administrative control and web access to users. A breakdown of the OpenStack services is given in Table I. Nova is a core component among them. It is designed to manage and automate pools of compute resources and can work with widely available virtualization technologies, as well as bare metal and high-performance computing (HPC) configurations.

#### *B. Single Root I/O Virtualization (SR-IOV)*

Single Root I/O Virtualization (SR-IOV) is a PCI Express (PCIe) standard which specifies the native I/O virtualization capabilities in PCIe adapters. As the solid line shown in Figure 1(a), SR-IOV allows a single physical device, or a Physical Function (PF), to present itself as multiple virtual devices, or Virtual Functions (VFs). Each virtual device can be dedicated to a single VM through PCI pass-through which allows each VM to directly access the corresponding VF. SR-IOV is a hardware-based approach to implement I/O virtualization which means drivers of the PF can also be used to drive the VFs.

## *C. Inter-VM Shared Memory (IVShmem)*

IVShmem (e.g. Nahanni) [21] provides zero-copy access to data co-residing on VM shared memory, for guest-toguest and host-to-guest communications. IVShmem is mainly designed and implemented on the system call layer and its interfaces are visible to user space applications as well. As the dash line shown in Figure 1(a), the shared memory region is allocated by host POSIX operations and mapped to the QEMU process' address spaces. The mapped memory can be used for guest applications by being mapped to guest user space. Through supporting zero-copy, IVShmem can achieve better performance.

TABLE I: OpenStack Services

| Service | Project name | Description |
| --- | --- | --- |
| Dashboard | Horizon | Provides a web-based self-service portal to interact with underlying OpenStack services. |
| Compute | Nova | Manages the lifecycle of compute instances in an OpenStack environment. |
| Networking | Neutron | Enables network connectivity as a service for other OpenStack services. |
| Object Storage | Swift | Swift Stores and retrieves arbitrary unstructured data objects. |
| Block Storage | Cinder | Provides persistent block storage to running instances. |
| Identity Service | Keystone | Provides an authentication and authorization service for other OpenStack services. |
| Image Service | Glance | Stores and retrieves virtual machine disk images. |
| Telemetry | Ceilometer | Monitors and meters the OpenStack cloud for billing, benchmarking, scalability, and statistical purposes. |
| Orchestration | Heat | Orchestrates multiple composite cloud applications. |

![](_page_2_Figure_2.png)

Fig. 1: Overview of Communication Channels(SR-IOV, IVShmem) and OpenStack

# *D. InfiniBand*

InfiniBand [13] is an industry standard switched fabric designed for interconnecting nodes in HPC clusters. The TOP500 rankings released in November 2014 indicate that 45% of the computing systems use InfiniBand as their primary interconnect. Remote Direct Memory Access (RDMA) is one of the main features of InfiniBand, which allows the process to remotely access memory contents of another remote process without any involvement at the remote side.

#### *E. Amazon EC2*

Amazon Elastic Compute Cloud (Amazon EC2) [1] is a web service that provides resizable compute capacity in the cloud. The EC2 cloud offers a wide range of vCPU, memory, and disk options as well as several different operating systems. For HPC field, C3 instances, as the compute-optimized instances, provide customers with the highest performing processors and enhanced networking capabilities. Currently, there are 5 models for C3 instances. The instance configuration including number of vCPU, memory size and storage size varies according to different models. All C3 models use Intel Xeon E5-2680 v2 (Ivy Bridge) and SR-IOV enabled 10 GigE technology.

# III. PROPOSED DESIGN

In this section, we first describe the architecture of a basic HPC cloud deployed by OpenStack. Then, we present the extension to the current OpenStack framework to enable our IVShmem support. Finally, we discuss and analyze design alternatives for the MPI library to support locality aware communication on HPC clouds.

## *A. Building HPC Cloud with MVAPICH2 over OpenStack*

OpenStack is used to build our private cloud. In our HPC cloud deployment, we use a four-node architecture with legacy networking. As shown in Figure 2, one node serves as a controller node, others serve as compute nodes. In Figure 2, we show our OpenStack deployment for future reference. On the controller node, we start basic supporting services, identity service, image service and the compute management service. As we introduced in Section II-A, the identity service provides the necessary authorization and authentication functionality for other OpenStack services in our HPC cloud. The image service manages the disk image of the VM. In our HPC cloud deployment, we upload an 8GB VM image file to the image service, which includes the RHEL 6.5 OS and some necessary tools for building MVAPICH2 library. The compute management service will schedule the VM on one compute node and supervise the lifecycle of the VM instance.

The compute services run on each compute node. One such service, nova-network, handles the VM networking, while nova-compute is the primary daemon, which creates and terminates virtual machines instances through libvirt.

For each VM, we configure two network interfaces, Ethernet and InfiniBand. Through nova-network, we specify Flat-DHCP network mode to configure the Ethernet interface for all VMs. That is, the virtual Ethernet interface of each VM will be attached to the local bridge (br100) and get a valid IP address from the running DHCP server to enable network access. Security group rules can be applied here to support network access at different levels. In addition, we enable the PCI Passthrough capability by specifying the product and vendor ID of a PCI device during configuration time of the Nova system. So each virtual function of a specified SR-IOV enabled HCA will be passed through to each VM during VM launch time.

Once the virtual InfiniBand network across the VMs is active, the high performance communication network of our HPC cloud is set up. MVAPICH2 (shown as MV2), as an MPI library, can be configured and run over this virtual InifiniBand network in our HPC cloud.

![](_page_3_Figure_2.png)

Fig. 2: Overview of HPC Cloud Architecture with MVAPICH2 over Openstack

#### *B. Extension to OpenStack*

Although IVShmem can significantly improve the performance of intra-node inter-VM communications compared to pure SR-IOV on virtualized InfiniBand clusters, the current OpenStack framework does not support it. Thus, it is necessary to extend OpenStack to support IVShmem. Figure 3 describes the basic logical architecture of the OpenStack Nova service. Note that there are two supporting services, message queue (AMQP) and the database (Nova-Database). These two components facilitate the asynchronous orchestration of complex tasks through message passing and information sharing. In this figure, Nova-api provides an endpoint for all API queries (either OpenStack API or EC2 API) and initiates most of the orchestration activities (such as running an instance). Nova-Scheduler, takes a virtual machine instance request from the queue and determines where it should run. Nova-Network mainly accepts networking tasks from the queue and then manipulates the network accordingly. Nova-Compute serves primarily as a worker daemon that creates and terminates virtual machine instances. In this process, Nova-Compute will accept instance configuration requests from the user or other services and convert them into XML files. Nova-Compute then invokes the libvirt library to parse the XML file and launch the desired virtual machine instance. To enable IVShmem support, we add an IVShmem format function when Nova configures the virtual machine instance for libvirt, as shown in Listing 1. This function is responsible for converting IVShmem requests to the QEMU namespace XML format for the guest VM.

![](_page_3_Figure_7.png)

Fig. 3: IVShmem Extension in Nova Architecture

#### Listing 1: Add IVShmem Format Function

| class LibvirtConfigGuest(LibvirtConfigObject): |
| --- |
| def __init__(self, **kwargs): |
| def _format_basic_props: |
| def _format_os: |
| def _format_features: |
| def _format_cputune: |
| def _format_devices: |
| # Add IVShmem support here |
| def _format_ivshmem: |
| def format_dom: |
| def parse_dom: |

### *C. Locality Aware Design Alternatives*

Based on our HPC cloud deployed by OpenStack and IVShmem extension, each VM has both SR-IOV and IVShmem enabled. However, only having IVShmem support is not enough for executing high performance intra-node inter-VM shared memory communication. We still lack an effective way to detect co-located VMs on the same host in order to trigger shared memory based communication. Therefore, designing a locality aware mechanism for our HPC cloud becomes a critical issue. Basically, there are two types of locality identification schemes.

The first type is based on the static method, which is mainly used when the information of co-resident VMs is preconfigured by the administrator, and it is assumed that VM host does not change. Thus, the VM locality information is already available at the beginning. The advantage of this approach is that the processes can be directly re-organized and re-mapped for VMs based on the above locality information, with little overhead. In HPC cloud environments, the controller node will play the role of administrator, as shown by arrow 1 in Figure 4. The disadvantage of this approach is that if a failure or timeout happens during the communication between the controller node and compute node, it can not update the locality information timely and correctly. Another possibility is that if too many locality information requests come to the compute service, it may become a bottleneck on the HPC cloud.

The other method is dynamic detection, that is, MPI jobs will dynamically detect the VMs running on the same host. There are two ways to achieve this. The first one is based on the IB connection, as arrow 3 shows in Figure 4. Since the virtual IB network is active, we can initiate a collective communication across all VM instances to acquire the locality information. Although this communication can take advantage of existing virtual IB networks, collective communication will incur much overhead. The second dynamic detection method is based on a shared memory region located on the same physical host, as arrow 2 shows in Figure 4. Each VM can acquire the locality information by accessing this shared memory region. IVShmem is a good candidate for this. As introduced in Section II-C, IVShmem provides a mechanism which is able to expose host shared memory regions to those VMs running on the same physical host. Thus, co-located VMs can be aware of each other by using this shared memory region. In this approach, we avoid unnecessary communication, possible failure issues and bottlenecks Therefore, locality information can be acquired and updated in a timely manner.

We have proposed our design to enable the high performance MPI library, MVAPICH2, to take advantage of this capability of IVShmem on SR-IOV enabled InfiniBand clusters [15]. As shown in Figure 4, in our design two key components 'Communication Coordinator' and 'Locality Detector' are added between the ADI3 layer and channel layer of the MVAPICH2 stack.

The Locality Detector maintains the information of local VMs on the same host based on a shared memory region exposed by IVShmem. The Communication Coordinator is responsible for capturing the communication channel requests coming from the upper layer and carrying out the channel selection by checking the locality information provided by the Locality Detector. If the communicating processes are coresident, the Communication Coordinator will schedule them to communicate through the IVShmem channel. Otherwise, they will go through the SR-IOV channel.

![](_page_4_Figure_3.png)

Fig. 4: Virtual Machine Aware MVAPICH2 Design

#### IV. A CASE STUDY OF BUILDING A PRIVATE HPC CLOUD IN NOWLAB

Through the IVShmem extension in the OpenStack Nova system and locality aware communication design for MVA-

TABLE II: Configurations of Test Clusters

| Cluster | Nowlab HPC Cloud |  | EC2 |  |
| --- | --- | --- | --- | --- |
| Instance | 4Cores/VM | 8Cores/VM | 4Cores/VM | 8Cores/VM |
| Platform | RHEL 6.5 Qemu+KVM |  | Amazon | Amazon |
|  | HVM |  | Linux | Linux |
|  |  |  | (EL6) | (EL6) |
|  |  |  | Xen HVM | Xen HVM |
|  |  |  | c3.xlarge | c3.2xlarge |
|  |  |  | Instance | Instance |
| CPU | SandyBridge | Intel(R) | IvyBridge Intel(R) Xeon |  |
|  | Xeon E5-2670 (2.6GHz) |  | E5-2680v2 (2.8GHz) |  |
| RAM | 6GB | 12GB | 7.5GB | 15GB |
| Interconnect | FDR(56Gbps) |  | 10GbE with Intel ixg |  |
|  | InfiniBand | Mellanox | bevf SR-IOV driver |  |
|  | ConnectX-3 with SR |  |  |  |
|  | IOV |  |  |  |

PICH2 library, we are ready to build our private HPC cloud. In this section, we build an experimental HPC cloud with MVAPICH2 over OpenStack, named Nowlab HPC Cloud.

The Nowlab cloud consists of four nodes. Each of them has dual 8-core 2.6 GHz Intel Xeon E5-2670 (Sandy Bridge) processors, 32 GB main memory and is equipped with Mellanox ConnectX-3 FDR (56 Gbps) HCAs with PCI Express Gen3 interfaces. The other cloud is based on a Compute Optimized instance(C3) from Amazon Elastic Compute Cloud, EC2.

The detailed instance configurations of these two HPC clouds are listed in Table II. As shown in Table II, each cloud has two types of instances, 4 cores/VM and 8 cores/VM, in order to be consistent with c3.xlarge and c3.2xlarge instance on EC2. These two HPC clouds are used as two testbeds for conducting the following performance evaluation.

Our OpenStack-based HPC cloud deployment reduces the configuration time from several hours to several minutes. All the deployment tools are publicly available and easy to use. Consequently, the complexity of building a highly-efficient HPC cloud is significantly reduced.

#### V. EVALUATION

Based on the above-mentioned Nowlab HPC cloud and popular Amazon EC2 cloud, we use MVAPICH2 2.0 as the high performance MPI library and OSU Micro-Benchmarks (OMB) 4.3 to conduct all the performance evaluations below. Note that we can not launch more than four C3 instances at the same time because of the account limit on EC2. Therefore, we only present EC2 performance at four VMs scale on collective and application performance sections. In the following evaluations, MV2-EC2 represents the performance on EC2 cloud, MV2-SR-IOV-Def represents SR-IOV enabled InfiniBand performance on Nowlab HPC cloud, MV2-SR-IOV-Opt represents our optimized design, which is the performance under the support of SR-IOV enabled InfiniBand and IVShmem. Lastly, MV2-Native refers to bare-metal performance of MVAPICH2 library over InfiniBand without virtualization.

# *A. Point-to-Point Communication Performance*

In this section, we evaluate MPI Point-to-Point communication performance for inter-VM in terms of latency and bandwidth. We launch two VMs with four cores each on one node of the Nowlab HPC Cloud and two c3.xlarge instances on EC2. In order to get better performance on Amazon EC2, we utilize 'Placement Groups' service, do the evaluation on multiple sets of VMs and take the best ones as the final results for our evaluation.

Figure 5(a) and Figure 5(b) show the Point-to-Point performance for intra-node inter-VM communication. From these two figures, we can observe that with the support of locality aware MPI communication, our design can significantly enhance the point-to-point performance over SR-IOV. We see improvements up to 84% and 158% in terms of latency and bandwidth, respectively. If we compare the performance between our design and native MPI, the results show that our design only has 3-8% overhead over native performance, which is much smaller than the overhead of SR-IOV. For instance, the MPI point-to-point latency of SR-IOV is around 1.2μs at 8Byte message sizes, while the latencies of our design and the native mode are 0.23μs and 0.22μs, respectively. In this case, our design incurs about 5% overhead. In addition, we also evaluate the point-to-point performance between two EC2 c3.xlarge instances. The red lines in Figure 5(a) and Figure 5(b) indicate that there is huge performance gap between EC2 and our HPC cloud. Although the interconnect on our cloud is 5.6X the theoretical speed of EC2, our design can bring up to 160X and 28X improvements for latency and bandwidth by locality aware communication support. For example, the peak bandwidth on EC2 is around 400MB/s, while our design is able to achieve 9.5GB/s. Through the above comparison, we can clearly see the significant performance benefits and minor overhead by incorporating locality aware communication into the MPI library over virtualized environments.

#### *B. One-Sided Communication Performance*

Figure 6 shows the One-Sided point-to-point performance for intra-node inter-VM communication. From Figure 6(a) and Figure 6(b), we can see that compared with the SR-IOV scheme, our locality aware design shows up to 63% and 42% improvements in terms of put latency and put bandwidth, respectively. For example, the put latency of SR-IOV at 8Byte message sizes is 1.38μs, while it is only 0.53μs for the locality aware design. If we compare the performance between our design and EC2 platform, the result shows that locality aware design can improve put latency and put bandwidth by a factor of 134X and 33X, respectively.

For the one-sided get operation, as we can see from Figure 6(c) and Figure 6(d), both get latency and get bandwidth can be improved up to 70% by our design, compared with SR-IOV scheme. If we compare the performance of our design with that on EC2 platform, the result shows that with the help of locality aware communication, the get latency can be reduced by a factor of 121X, while get bandwidth can be improved by a factor of 24X.

## *C. Collective Communication Performance*

In this section, we evaluate the communication performance on four commonly used collective operations with 4 cores/VM on these two clouds. It consists of two different scales. One has 16 processes across four VMs, the other has 64 processes across 16 VMs.

*1) Collective Performance on four VMs:* From Figure 7(a)- Figure 7(d), we can observe that with four VMs, our design can effectively improve the collective communication performance, compared with SR-IOV. The improvement can be up to 74%, 60%, 74% and 81%, for MPI Bcast, MPI Allreduce, MPI Allgather and MPI Alltoall, respectively. For example, the latency of MPI Bcast at 512Byte message sizes is around 4.37μs for SR-IOV, while it is only 1.13μs for our design. We also evaluate the performance of these four collective communication operations with four c3.xlarge instances on EC2. Compared with EC2 performance, from Figure 7(a)- Figure 7(d), we can see that the locality aware communication design can have significant performance improvement. From 1Byte to 1MB message sizes, the improvement can be up to a factor of 65X, 22X, 28X and 45X, for MPI Bcast, MPI Allreduce, MPI Allgather and MPI Alltoall, respectively.

*2) Collective Performance on 16 VMs:* In order to evaluate collective communication performance at a larger scale, we launch 16 VMs across all three compute nodes and one controller node on the Nowlab HPC Cloud. As we can see from Figure 8(a)-Figure 8(d), the locality aware design can still clearly benefit MPI collective communications, compared with SR-IOV. The evaluation results show that the improvement can be up to 41%, 45%, 40% and 39%. Note that the improvement percentages drop for all the above four collective operations, compared with four VMs case. That is because the portion of shared memory communication is decreased as the VM scale keeps increasing. The benefit we can gain from shared memory based communication is also decreased accordingly.

The evaluation results indicate that with locality aware MPI communication support, the MPI collective communication can be greatly improved. It can bring us huge communication performance enhancements, especially on cloud computing platform, such as Amazon EC2.

## *D. Application Performance*

In this section, we present our evaluation with two HPC applications: NAS and Graph500. These two applications involve multiple MPI communication patterns, including MPI Allreduce, MPI Alltoall, MPI Bcast, MPI Send/MPI Isend, MPI Recv/MPI Irecv, etc [6]. Therefore, we are able to evaluate our locality aware communication design and SR-IOV scheme. The evaluation are conducted with 8 cores/VM configuration on these two clouds. Similarly with Section V-C, four instances are launched on the Nowlab HPC Cloud and Amazon EC2 first. Then to evaluate the application performance at larger scale, eight instances are deployed across all four nodes of the Nowlab HPC Cloud.

Figure 9(a) presents the performance comparison of Class B NAS benchmarks among SR-IOV scheme, locality aware design, native, and EC2. The evaluation results indicate that the locality aware design only incurs minor overhead, FT(9%), CG(2%), LU(3%), EP(2%), compared with native performance. Moreover, compared with EC2 performance, locality aware design can deliver up to 77%(FT), 39%(CG), 32%(LU) and 12%(EP) improvement. As shown in Figure 9(b), Graph500 evaluation result shows that for different

![](_page_6_Figure_0.png)

Fig. 5: Point-to-Point Performance

![](_page_6_Figure_2.png)

Fig. 6: One-Sided Performance

problem size, locality aware design can reduce the execution time by up to a factor of 12X, compared with the result on EC2, while only incurring around 6% overhead, compared with native.

To further evaluate the performance impact of locality aware design on these two applications at larger scale, we launch eight VMs on the Nowlab HPC Cloud, which involves all 64 cores. The Class C NAS benchmarks evaluations, as shown in Figure 9(c), indicate that locality aware design merely introduces around 6-9% overhead, compared with native performance. From the Graph500 evaluation results in Figure 9(d), we can see that the execution times at different problem sizes based on locality aware communication design are merely increased by around 8%, compared with native performance. According to the above performance evaluation results, high performance MPI libraries with locality aware communication support can dramatically cut down the execution time of real HPC applications, compared with the results on currently popular EC2 platform. Meanwhile, it only introduces minor overhead, compared with native performance.

## VI. RELATED WORK

On the aspect of cloud computing, Nimbus [18] provides a toolkit for building the IaaS cloud. It leverages virtualization hypervisors and virtual machine schedulers to allow deployment of self-configured virtual clusters via contextualization. There are similar systems such as Eucalyptus [3], OpenNebula [4] and OpenStack. Lu et al. [28], [14] presented a live system, Vega LingCloud, and associated asset-leasing model to provide a Resource Single Leasing Point System for con-

![](_page_7_Figure_0.png)

Fig. 8: Collective Communication Performance on 16 VMs (4 cores/VM)

![](_page_8_Figure_0.png)

Fig. 9: Application Performance

solidated renting of physical and virtual machines on shared infrastructure. Crago et al. [26] extended the OpenStack cloud computing stack to support heterogeneous architectures and accelerators, like GPU. Recently, NSF announced an award for the Chameleon cloud testbed [2], which is a large-scale, reconfigurable experimental environment for next generation cloud research.

On the other hand, I/O virtualization schemes can be generally classified into software based and hardware based schemes. Earlier studies such as [22], [7] have shown network performance evaluations of software-based approaches in Xen. Studies [19], [8], [12] have proven that SR-IOV demonstrates significantly better performance, compared to software-based solutions for 10 GigE networks. Liu et al. [19] provided a detailed performance evaluation on the environment of SR-IOV capable 10 GigE in KVM. Studies [9], [10], [20], [11] with Xen demonstrate the ability to achieve near-native performance in VM-based environment for HPC applications. To improve inter-VM communication, the work [21] first presented the framework of Nahanni. Based on it, the MPI-Nahanni userlevel library was developed, which ported the MPICH2 library from the Nemesis channel that uses memory-mapped shared memory to Nahanni so that co-resident VM communication can be accelerated. However, the work of MPI-Nahanni did not involve SR-IOV technology and cloud computing environment.

In our earlier studies, we proposed Inter-VM Communi-

cation designs (IVC) with Xen, and redesigned MVAPICH2 library to leverage the features offered by the IVC [9]. However, this solution does not show the studies with SR-IOV enabled InfiniBand clusters. Our early evaluation on SR-IOV enabled InfiniBand cluster [17] shows that while SR-IOV enables low-latency communication, MPI libraries need to be redesigned carefully in order to provide advanced features to improve intra-node inter-VM communication. Our recent evaluation [16] has revealed that there is significant performance potential for IVShmem to improve intra-node inter-VM communication on SR-IOV enabled InfiniBand clusters. And we redesigned MVAPICH2 library to take advantage of this feature.

Therefore, to support high performance I/O virtualization in cloud computing environment, this paper focuses on presenting an efficient approach to build HPC clouds by extending Open-Stack and proposing VM locality aware MVAPICH2 library on the extended OpenStack-based HPC clouds.

#### VII. CONCLUSION AND FUTURE WORK

In this paper, we propose an efficient approach to build HPC Clouds by using MVAPICH2 over OpenStack with SR-IOV. In order to improve unsatisfactory inter-VM communication performance within the same physical node on a HPC Cloud, we extend OpenStack compute service (Nova) to enable IVShmem support. Through this, high performance MPI library can have SR-IOV channel for inter-node inter-VM communication as well as IVShmem channel for intranode inter-VM communication. We further discuss and analyze the multiple ways to enable inter-VM communication in MPI library to be locality aware on HPC Clouds. Among them, IVShmem based locality detection becomes an ideal method. Based on our extension to OpenStack and virtual machine locality aware design in MVAPICH2 library, we share our experiences on building an experimental local HPC Cloud, which shows that our proposed approach works efficiently. In our HPC Cloud, we conduct comprehensive performance evaluations by using point-to-point, collective benchmarks and HPC applications, and we further compare the performance on our HPC cloud with that on Amazon EC2.

Our performance evaluations show that compared with SR-IOV, the proposed locality aware communication design can significantly improve the intra-node inter-VM performance by up to 84% and 158% in terms of latency and bandwidth, respectively, while only incurring 3-8% overhead, compared to native performance. On the comparison with Amazon EC2, our design can bring up to 160X and 33X improvements for point-to-point latency and bandwidth, respectively. For collective operations on our HPC Cloud, the proposed design can improve Broadcast, Allreduce, Allgather and Alltoall up to 74%, 60%, 74%, and 81%, respectively, compared with the default SR-IOV scheme. Compared with the performance on Amazon EC2, the achieved improvements by our design can go up to 65X, 22X, 28X, and 45X, respectively. The application performance evaluations show that our proposed design can deliver near native performance with minor overhead on our HPC Cloud. Compared with EC2 performance, the execution time can be reduced by up to a factor of 12X. These comparison results indicate that future HPC clouds built upon MVAPICH2 over extended OpenStack with SR-IOV will attain much better performance compared with current generation clouds, such as Amazon EC2. In the future, this work will be installed on the NSF cloud testbed, Chameleon, to carry out further exploration in a large-scale experimental environment.

#### REFERENCES

- [1] "Amazon EC2," http://aws.amazon.com/ec2/.
- [2] "Chameleon," http://chameleoncloud.org/.
- [3] "Eucalyptus," http://eucalyptus.com/.
- [4] "OpenNebula," http://opennebula.org.
- [5] "OpenStack," http://openstack.org/.
- [6] A. Faraj, X. Yuan, "Communication Characteristics in the NAS Parallel Benchmarks," in *Proceedings of 14th IASTED International Conference on Parallel and Distributed Computing and Systems (PDCS)*, Cambridge, USA, November 4-6 2002.
- [7] P. Apparao, S. Makineni, and D. Newell, "Characterization of Network Processing Overheads in Xen," in *Proceedings of the 2nd International Workshop on Virtualization Technology in Distributed Computing*, ser. VTDC '06. Washington, DC, USA: IEEE Computer Society, 2006.
- [8] Y. Dong, X. Yang, J. Li, G. Liao, K. Tian, and H. Guan, "High Performance Network Virtualization with SR-IOV," *Journal of Parallel and Distributed Computing*, 2012.
- [9] W. Huang, M. J. Koop, Q. Gao, and D. K. Panda, "Virtual Machine aware Communication Libraries for High Performance Computing," in *Proceedings of the 2007 ACM/IEEE conference on Supercomputing*, ser. SC '07. New York, NY, USA: ACM, 2007, pp. 9:1–9:12.

- [10] W. Huang, J. Liu, B. Abali, and D. K. Panda, "A Case for High Performance Computing with Virtual Machines," in *Proceedings of the 20th Annual International Conference on Supercomputing*, ser. ICS '06, New York, NY, USA, 2006.
- [11] W. Huang, J. Liu, M. Koop, B. Abali, and D. Panda, "Nomad: Migrating OS-bypass Networks in Virtual Machines," in *Proceedings of the 3rd International Conference on Virtual Execution Environments*, ser. VEE '07, New York, NY, USA, 2007.
- [12] Z. Huang, R. Ma, J. Li, Z. Chang, and H. Guan, "Adaptive and Scalable Optimizations for High Performance SR-IOV," in *Proceeding of 2012 IEEE International Conference Cluster Computing (CLUSTER)*. IEEE, 2012, pp. 459–467.
- [13] Infiniband Trade Association, http://www.infinibandta.org.
- [14] J. Peng, X. Lu, B. Cheng, L. Zha, "JAMILA: A Usable Batch Job Management System to Coordinate Heterogeneous Clusters and Diverse Applications over Grid or Cloud Infrastructure," in *Proceedings of Network and Parallel Computing*, Zhengzhou, China, September 13- 15 2010.
- [15] J. Zhang, X. Lu, J. Jose, M. Li, R. Shi, D. K. Panda, "High Performance MPI Library over SR-IOV Enabled InfiniBand Clusters," in *Proceedings of International Conference on High Performance Computing (HiPC)*, Goa, India, December 17-20 2014.
- [16] J. Zhang, X. Lu, J. Jose, R. Shi, D. K. Panda, "Can Inter-VM Shmem Benefit MPI Applications on SR-IOV based Virtualized InfiniBand Clusters?" in *Proceedings of 20th International Conference Euro-Par 2014 Parallel Processing*, Porto, Portugal, August 25-29 2014.
- [17] J. Jose, M. Li, X. Lu, K. Kandalla, M. Arnold, and D. Panda, "SR-IOV Support for Virtualization on InfiniBand Clusters: Early Experience," in *Proceedings of 13th IEEE/ACM International Symposium Cluster, Cloud and Grid Computing (CCGrid)*, May 2013, pp. 385–392.
- [18] K. Keahey, I. Foster, T. Freeman and X. Zhang, "Virtual Workspaces: Achieving Quality of Service and Quality of Life in the Grid," *Sci. Program.*, vol. 13, no. 4, pp. 265–275, Oct. 2005.
- [19] J. Liu, "Evaluating Standard-Based Self-Virtualizing Devices: A Performance Study on 10 GbE NICs with SR-IOV Support," in *Proceeding of 2010 IEEE International Symposium Parallel & Distributed Processing (IPDPS)*. IEEE, 2010, pp. 1–12.
- [20] J. Liu, W. Huang, B. Abali, and D. K. Panda, "High Performance VMM-bypass I/O in Virtual Machines," in *Proceedings of the Annual Conference on USENIX '06 Annual Technical Conference*, ser. ATC '06, Berkeley, CA, USA, 2006.
- [21] A. C. Macdonell, "Shared-Memory Optimizations for Virtual Machines," PhD Thesis. University of Alberta, Edmonton, Alberta, Fall 2011.
- [22] A. Menon, J. R. Santos, Y. Turner, G. J. Janakiraman, and W. Zwaenepoel, "Diagnosing Performance Overheads in the Xen Virtual Machine Environment," in *Proceedings of the 1st ACM/USENIX international conference on Virtual execution environments*, ser. VEE '05. New York, NY, USA: ACM, 2005, pp. 13–23.
- [23] MVAPICH2: High Performance MPI over InfiniBand and iWARP, http://mvapich.cse.ohio-state.edu/.
- [24] OpenMPI: Open Source High Performance Computing, http://www.open-mpi.org/.
- [25] M. Rosenblum and T. Garfinkel, "Virtual Machine Monitors: Current Technology and Future Trends," *Computer*, vol. 38, no. 5, pp. 39–47, 2005.
- [26] S. Crago, K. Dunn, P. Eads, L. Hochstein, D. Kang, M. Kang, D. Modium, K. Singh, J. Suh and J. Walters, "Heterogeneous Cloud Computing," in *Proceedings of 2011 IEEE International Conference on Cluster Computing (Cluster)*, Austin, TX, USA, September 26-30 2011.
- [27] Single Root I/O Virtualization, http://www.pcisig. com/specifications/iov/single root.
- [28] X. Lu, J. Lin, L. Zha and Z. Xu, "Vega LingCloud: A Resource Single Leasing Point System to Support Heterogeneous Application Modes on Shared Infrastructure," in *Proceedings of IEEE 9th International Symposium on Parallel and Distributed Processing with Applications*, Busan, Korea, May 26-28 2011.

