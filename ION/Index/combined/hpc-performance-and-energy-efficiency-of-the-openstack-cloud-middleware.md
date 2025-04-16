# HPC Performance and Energy-Efficiency of the OpenStack Cloud Middleware

Sébastien Varrette∗, Valentin Plugaru∗, Mateusz Guzek†, Xavier Besseron‡ and Pascal Bouvry∗ ∗Computer Science and Communications (CSC) Research Unit

†Interdisciplinary Centre for Security Reliability and Trust

‡Research Unit in Engineering Science

6, rue Richard Coudenhove-Kalergi, L-1359 Luxembourg, Luxembourg

Sebastien.Varrette@uni.lu, Valentin.Plugaru@gmail.com, Mateusz.Guzek@uni.lu, Xavier.Besseron@uni.lu, Pascal.Bouvry@uni.lu

*Abstract*—Since its advent in the middle of the 2000's, the Cloud Computing (CC) paradigm is increasingly advertised as THE solution to most IT problems. While High Performance Computing (HPC) centers continuously evolve to provide more computing power to their users, several voices (most probably commercial ones) emit the wish that CC platforms could also serve HPC needs and eventually replace in-house HPC platforms. However, it is still unclear whether the overhead induced by the virtualization layer at the heart of every Cloud middleware suits an environment as high-demanding as an HPC platform. In parallel, with a growing concern for the considerable energy consumed by HPC platforms and data centers, research efforts are targeting green approaches with higher energy efficiency. At this level, virtualization is also emerging as the prominent approach to reduce the energy consumed by consolidating multiple running VM instances on a single server, thus giving credit towards a Cloud-based approach. In this paper, we analyze from an HPC perspective the performance and the energy efficiency of the leading open source Cloud middleware, OpenStack, when compared to a bare-metal (*i.e.* native) configuration. The conducted experiments were performed on top of the Grid'5000 platform with benchmarking tools that reflect "regular" HPC workloads, *i.e.* HPCC (which includes the reference HPL benchmark) and Graph500. Power measurements were also performed in order to quantify the potential energy efficiency of the tested configurations, using the approaches proposed in the Green500 and GreenGraph500 projects. In order to abstract from the specifics of a single architecture, the benchmarks were run using two different hardware configurations, based on Intel and AMD processors. This work extends previous studies dedicated to the evaluation of hypervisors against HPC workloads. The results of this study pleads for in-house HPC platforms running without any virtualized frameworks, assessing that the current implementation of Cloud middleware is not well adapted to the execution of HPC applications.

#### I. INTRODUCTION

Many organizations have departments and workgroups that benefit (or could benefit) from High Performance Computing (HPC) resources to analyze, model, and visualize the growing volumes of data they need to conduct business. Actually, HPC remains at the heart of our daily life in widespread domains as diverse as molecular dynamics, structural mechanics, computational biology, weather prediction or "simply" data analytics. Also, domains such as applied research, digital health or nanoand bio- technology will not be able to evolve tomorrow without the help of HPC. In this context, and despite the economical crisis, massive investments (1 billion dollars or more) have been approved last year (in 2012) by the main leading countries or federations (US, Russia, China, India or the European Union) for programs to build an Exascale platform by 2020. This ambitious goal comes with a growing concern for the considerable energy consumed by HPC platforms and data centers, leading to research efforts toward green approaches with higher energy efficiency. Hardware improvements that use for instance low power processors or accelerators are out of the scope of this work. Here, our focus is on the middleware level where virtualization – the backend of any Cloud solution – is emerging as the prominent approach to minimize the energy consumed by consolidationg multiple running Virtual Machines (VMs) instances on a single server, while abstracting from the underlying hardware. However, little understanding has been obtained about the potential overhead in energy consumption and the throughput reduction for virtualized servers and/or computing resources, nor if it simply suits an environment as high-demanding as a High Performance Computing (HPC) platform. Only recently, some studies [1], [2] highlight a potential non-negligible overhead for HPC workloads when running on top of the three most widespread virtualization frameworks, namely Xen, KVM, and VMware ESXi.

In parallel, this question is connected with the rise of Cloud Computing (CC), increasingly advertised as THE solution to most IT problems. Several voices (most probably commercial ones) emit the wish that CC platforms could also serve HPC needs and eventually replace in-house HPC platforms. In order to assess this latter idea, we initiate a general study on Cloud systems featuring HPC workloads. This paper comes in this context. While we tackled hypervisor evaluation in our precedent studies, we propose here a deep analysis of the leading open source Cloud middleware OpenStack [3] when confronted with typical HPC usage. More precisely, we analyze the HPC Challenge (HPCC) benchmark performance and the energy profile of OpenStack on top of the Xen and KVM hypervisors, and compare these configurations with a *baseline* environment running in native mode. The experiments performed in this paper were conducted on the Grid'5000 platform [4], which offers a flexible and easily monitorable environment that helped refine the holistic model for the power consumption of HPC components which was proposed in [1]. Grid'5000 also features an unique environment as close as possible to a real HPC system, even if we were limited in the number of resources we managed to deploy for this study.

![](_page_0_Picture_12.png)

Thus, while the context and the results presented in this article do not reflect a true large scale environment (we never exceed 72 nodes whether virtual or physical in the currently presented experiments), we still think that the outcomes generated by this study are of benefit for the HPC community.

The contributions of this work cover four aspects. First, our original methodology allows to perform an automated, reproducible and fair comparison of different VM configurations deployed through the OpenStack middleware in an HPC environment. Then, we provide performance numbers for two reference benchmarking suites, HPCC and Graph500, running on OpenStack with two major hypervisors (Xen and KVM) and extend previous works to multiple node executions. Furthermore, the power consumption is measured and allows an energy efficiency evaluation according to the "Performance per Watt" metric defined in the Green500 and GreenGraph500 projects. Finally, to abstract from the specifics of a single architecture, the benchmarks were run using two different hardware configurations, based on Intel and AMD processors.

This article is organized as follows. Section II presents the background of this study. The experimental methodology is described in Section IV, in particular the benchmark workflow applied to operate the fair comparison of hypervisors. Then Section V details and discusses the experimental results obtained with the HPL benchmark on the selected environments. Finally, Section III reviews the related work and Section VI concludes the paper and provides some future directions and perspectives opened by this study.

## II. BACKGROUND

A new concept called Cloud Computing (CC) [5], [6] has recently emerged in heterogeneous distributed computing. In this paradigm, shared IT resources are dynamically allocated to customer tasks and environments. It allows users to run applications or even complete systems on demand by deploying them on the Cloud that acts like a gigantic computing facility. In particular, customers simply pay for what they use in service models generally defined as Software/Platform/Infrastructure/Network as a Service (SaaS, PaaS, IaaS, NaaS). CC is often viewed as the next IT revolution, similar to the birth of the Web or the e-commerce. All major vendors such as Google, Apple, Microsoft or Amazon now propose or push for this kind of service, with more and more success. Undoubtedly, CC platforms are about to become the core component of the next generation of IT services and devices, mainly because they formalize a concept that reduces computing costs at a time where computing power is primordial to reach competitiveness. In parallel, many organizations have departments and workgroups that benefit (or could benefit) from High Performance Computing (HPC) resources to analyze, model, and visualize the growing volumes of data they need to conduct business. Yet the issue of whether CC is suitable for HPC workloads remains unclear. In this context, this work analyzes from an HPC perspective the performance and the energy efficiency of the most widespread Cloud middleware for Infrastructure-asa-Service (IaaS) platforms, OpenStack, when compared to a native configuration. We focus on the IaaS level as it is the closest possible to the hardware. It enables the deployment and the execution of VMs controlled by an hypervisor or Virtual Machine Manager. There exist two types of hypervisors (either *native* or *hosted*) yet only the first class (also named baremetal) presents an interest for the HPC context. Among the many potential approaches of this type available today, the virtualization technology of choice for most open platforms over the past 7 years has been the Xen hypervisor [7]. More recently, the Kernel-based Virtual Machine (KVM) [8] has also known a widespread deployment within both the Cloud middleware and HPC community such that we limited our study to those two hypervisors and decided to place the other virtualization backends that OpenStack can use (such as VMWare ESX and Microsoft's Hyper-V, see Table II) out of the scope of this paper. Table I provides a short comparison chart between the Xen and KVM versions considered in this study. The main CC IaaS middlewares are listed in Table II.

Table I. OVERVIEW OF THE CONSIDERED HYPERVISORS CHARACTERISTICS.

| Hypervisor: | Xen 4.1 | KVM 84 |
| --- | --- | --- |
| Host architecture | x86, x86-64, ARM | x86, x86-64 |
| VT-x/AMD-v | Yes | Yes |
| Max Guest CPU | 128 (HVM), >255 (PV) | 64 |
| Max. Host memory | 5TB | equal to host |
| Max. Guest memory | 1TB (HVM), 512GB (HVM) | 512GB |
| 3D-acceleration | Yes (HVM) | No |
| License | GPL | GPL/LGPL |

Among the most recent IaaS frameworks, initially developed by NASA and Rackspace, OpenStack has quickly gathered the support of many technology companies [9] and has become the prominent open source Cloud solution. It currently has the backing of more than 250 companies and features API compatibility with other Cloud solutions such as Eucalyptus and Amazon's EC2 and S3 services. For these reasons OpenStack has been selected as the test platform in the present study.

#### *A. The Grid'5000 Testbed*

To reflect a traditional HPC environment, yet with a high degree of flexibility as regards the deployment process and the fair access to heterogeneous resources, the experiments presented in this paper were carried on the Grid'5000 platform [4]. Grid'5000 is a scientific instrument for the study of large scale parallel and distributed systems. It aims at providing a highly reconfigurable, controllable and monitorable experimental platform to support experiment-driven research in all areas of computer science related to parallel, large-scale or distributed computing and networking [10]. The infrastructure of Grid'5000 is geographically distributed on different sites hosting the instrument, initially 9 sites in France (10 since 2011), but also abroad. In total, Grid'5000 features 7896 computing cores over 26 clusters. The infrastructure offers both Myrinet and Infiniband networks, as well as Gigabit Ethernet. The sites are interconnected through a dedicated 10 Gb/s wide area network operated by Renater in France and Restena in Luxembourg. One of the unique features offered by this infrastructure compared to a production cluster is the possibility to provision on demand the Operating System (OS) running on the computing nodes. Designed for scalability and a fast deployment, the underlying software, named Kadeploy [11], supports a broad range of systems (Linux, Xen, *BSD, etc.) and manages a large catalog of images, most of them userdefined, that can be deployed on any of the reserved nodes of

| Middleware: | vCloud | Eucalyptus | OpenNebula | OpenStack | Nimbus |
| --- | --- | --- | --- | --- | --- |
| License | Proprietary | BSD License | Apache 2.0 | Apache 2.0 | Apache 2.0 |
| Supported | VMWare/ESX | Xen, KVM, | Xen, KVM, | Xen, KVM, | Xen, KVM |
| Hypervisor |  | VMWare | VMWare | Linux Containers, |  |
|  |  |  |  | VMWare/ESX, |  |
|  |  |  |  | Hyper-V,QEMU, UML |  |
| Last Version | 5.5.0 | 3.4 | 4.4 | 8 (Havana) | 2.10.1 |
| Programming | n/a | Java / C | Ruby | Python | Java / Python |
| Language |  |  |  |  |  |
| Host OS | VMX server | RHEL 5, ESX | RHEL 5, | Ubuntu, ESX | Ubuntu, |
|  |  | Debian, Fedora, | Debian, Fedora, | Debian, | Debian, |
|  |  | CentOS 5, openSUSE-11 | CentOS 5,openSUSE-11 | RHEL, SUSE, Fedora | RHEL, SUSE, Fedora |
| Guest OS | Windows (S2008,7), | Windows (S2008,7), | Windows (S2008,7), | Windows (S2008,7), | Windows (S2008,7), |
|  | openSUSE,Debian,Solaris | openSUSE,Debian,Solaris | openSUSE,Debian,Solaris | openSUSE,Debian,Solaris | openSUSE,Debian,Solaris |
| Contributors | VMWare | Eucalyptus systems, | C12G Labs, | Rackspace, IBM, HP, Red Hat, SUSE, | Community |
|  |  | Community | Community | Intel, AT&T, Canonical, Nebula, others |  |

Table II. SUMMARY OF DIFFERENCES BETWEEN THE MAIN CC MIDDLEWARES.

the platform. As we will detail in Section IV, we have defined a set of common images and environments to be deployed to perform (and eventually reproduce) our experiment. As this study also focuses on the energy consumption, power measures were required such that we had to select a site where Power Distribution Units (PDUs) measurements were available. For this purpose, the sites of Lyon and Reims were chosen.

#### *B. Considered HPC Performance benchmarks*

Several benchmarks that reflect a true HPC usage were selected to compare all of the considered configurations. For reproducibility reasons, all of them are open source and we based our choice on a previous study operated in the context of the FutureGrid platform [12], and a better focus on I/O operation that we consider as under-estimated in too many studies involving virtualization evaluation. We thus arrived to the following benchmarks:

- The HPC Challenge (HPCC) [13], an industry standard suite used to stress the performance of multiple aspects of an HPC system, from the pure computing power to the RAM usage or the network communication efficiency. It also provides reproducible results, at the heart of the ranking proposed in the Top500 project.
- Graph500 [14] a recent benchmark for data-intensive applications, which stresses the communication subsystem of the system, instead of counting double precision floating-point like in HPL. It is based on a breadth-first search in a large undirected graph and reports various metrics linked to the underlying graph algorithm, the main one being measure in GTEPS (109 Traversed Edges Per Second).

In practice, HPCC basically consists of seven tests: (1) HPL (the High-Performance Linpack benchmark), which measures the floating point rate of execution for solving a linear system of equations; (2) DGEMM, which measures the floating point rate of execution of double precision real matrix-matrix multiplication; (3) STREAM, a simple synthetic benchmark program that measures sustainable memory bandwidth (in GB/s) and the corresponding computation rate for simple vector kernel; (4) PTRANS (parallel matrix transpose), which exercises the communications where pairs of processors communicate with each other simultaneously. It is a useful test of the total communications capacity of the network; (5) RandomAccess that measures the rate of integer random updates of memory (GUPS); (6) FFT which evaluate the floating point rate of execution of double precision complex one-dimensional Discrete Fourier Transform (DFT). The last test (PingPong) measures the latency and bandwidth of a number of simultaneous communication patterns.

In all cases, the results that are obtained from all considered benchmarks provide an unbiased performance analysis of the configurations considered.

#### *C. Considered Energy-Efficiency benchmarcks*

For decades, the notion of HPC performance has mainly been synonymous with speed (as measured in Flops – floatingpoint operations per second). In order to raise awareness of other performance metrics of interest (e.g. performance per watt and energy efficiency for improved reliability), the Green500 project [15] was launched in 2005. Derived from the results of the Top500 – and thus on HPL measures, this list encourages supercomputing stakeholders to produce more energy efficient machines. The same approach has been proposed in the context of the Graph500 benchmark, leading to the Green Graph 500 [16] list which collects similarly performance-per-watt metrics and acts as a forum for vendors and data center operators to compare the energy consumption of data intensive computing workloads on their architectures.

We will show in Section V an energy-efficiency analysis based on the very same metric used in the Green500 and GreenGraph500 projects.

## III. RELATED WORK

At the level of the pure hypervisor performance evaluation, many studies can be found in the literature that attempt to quantify the overhead induced by the virtualization layer. Yet the focus on HPC workloads is recent as it implies several challenges, from a small system footprint to efficient I/O mechanisms.

Early quantitative studies were proposed in 2006 by L. Youseff et al. [17], and in 2007 by A. Gavrilovska et al. [18]. While the claimed objective was to present opportunities for HPC platforms and applications to benefit from system virtualization, the practical experimentation in the latter work identified two main limitations of interest for HPC, to be addressed by the hypervisors: I/O operations and adaptation to multi-core systems. While the second point is now circumvented on the considered hypervisor systems, the first one remains challenging.

Another study that guided our benchmarking strategy and our experimental setup is the evaluation mentioned in the previous section that was performed on the FutureGrid platform [12]. The targeted hypervisors were Xen, KVM, and Virtual Box and a detailed performance analysis is proposed, concluding that KVM is the best overall choice for use within HPC Cloud environments. In [19], the authors evaluated the HPC Challenge benchmarks in several virtual environments, including VMware, KVM and VirtualBox. The experiments were performed on a rather limited platform (a single host featuring two four-core Intel Xeon X5570 processor) using Open MPI. They demonstrate a rather low (yet always present) overhead induced by the virtual environments, which becomes less significant with larger problem sizes. In [20] the authors focus on the impact of virtualization on NUMA architectures, testing Xen and KVM with the NAS Parallel Benchmarks, and report a significant performance degradation of up to 82% on KVM and 4X on Xen when the VMs span several CPU sockets. The experiments were done with varying numbers of VMs, however only on single nodes from three considered architectures.

Driven by the increasing adoption of Cloud services, recent works such as the one of A. Maranthe et al. [21] have endeavoured to quantify the impact of Cloud environments on HPC applications' performance. Their study, while larger scale than the one proposed in the current paper, compared different HPC clusters of the LLNL with Amazon EC2 instances. A direct comparison of the results was thus not possible due to the differences in the underlying platforms, and only the Xen hypervisor – on which the EC2 platform is based – was tested.

In [1], the main facets of an HPC usage were studied by running the HPCC, IOZone and Bonnie++ benchmarks. The three most widespread virtualization frameworks, Xen, KVM, and VMware ESXi were examined against a *baseline* environment running in native mode. The approach permitted the evaluation of both high-performance and high-throughput workloads. Also, to abstract from the specifics of a single architecture, the benchmarks were run using two different hardware configurations, based on Intel or AMD processors. The measured data was used to create a statistical holistic model for the power consumption of a computing node that takes into account impacts of its components utilization metrics, as well as used application, virtualization, and hardware. For this initial study, we performed our experiments on single hosts running a single VM instance. Later on, [2] extends this seminal work by evaluating a more realistic HPC workload that involves far more nodes (whether virtual or physical). Yet the focus there was only on the HPL benchmark.

In this article, we propose the performance and energyefficiency evaluation of the most widespread open source Cloud IaaS middleware i.e OpenStack – with both Xen and KVM hypervisors – when precedent studies used to restrict to the hypervisor level. Not only do we propose here a benchmarking campaign over the reference HPCC and Graph500 suites – thus covering the most representative HPC workloads – but we also perform the distributed execution of these benchmarks across many physical nodes (up to 12, each of them running up to 6 VMs).

## IV. EXPERIMENTAL METHODOLOGY

The experimental tests performed as part of the current study have been carried out on the Grid'5000 platform, using a heavily modified version of the OpenStack-campaign code. The objective of our methodology was to enable the automated deployment of the OpenStack IaaS middleware, provisioning a specified number of VMs with custom VCPU/memory/disk configurations and the execution of CPU/memory/IO intensive applications that stress the virtualization infrastructures, showing the combined overhead of the virtualization layer and the overhead of the cloud middleware. This methodology complements previous work [2] where a lightweight orchestration of VM deployment without relying on IaaS frameworks was implemented. The current benchmarking workflow is summarized in Figure 1 and shows the steps involved in the OpenStack deployment and benchmark execution. The experiments have been performed at the Lyon and Reims sites of the Grid'5000, where we selected two of the most modern HPC clusters available *i.e.* the Taurus and StRemi clusters. An overview of the computing nodes and software environment is provided in Table III. In the Taurus cluster each node features an Intel processor with a Sandy Bridge micro-architecture, thus each core performing theoretically a maximum of 8 double-precision floating point operations per cycle, while the processors of the StRemi cluster, based on the AMD Magny-Cours micro-architecture, can carry out 4.

Table III. EXPERIMENTAL SETUP FOR THE WORK PRESENTED IN THIS STUDY.

| Label | Intel | AMD |
| --- | --- | --- |
| Site | Lyon | Reims |
| Cluster | taurus | stremi |
| Max #nodes | 12 (+1 controller) | 12 (+1 controller) |
| Processor type | Intel Xeon | AMD Opteron |
| Processor model | E5-2630@2.3GHz | 6164 HE@1.7GHz |
| #cpus per node | 2 | 2 |
| #core per node | 12 | 24 |
| #RAM per node | 32 GB | 48 GB |
| Rpeak per node | 220.8 GFlops | 163.2 GFlops |
| Operating System (Hyp.) | Ubuntu 12.04 LTS, Linux 3.2 |  |
| Operating System (VM) | Debian 7.1, Linux 3.2 |  |
| Cloud middleware | OpenStack Essex |  |
| HPCC | 1.4.2 |  |
| Green Graph500 | 2.1.4 |  |
| OpenMPI | 1.6.4 |  |
| Intel Cluster Suite | 2013.2.146 |  |
| Intel MKL | 11.0.2.146 |  |

## *A. Benchmarking workflow*

For both baseline (*i.e.* without any cloud middleware nor virtualization layer installed) and OpenStack (with either Xen or KVM hypervisors) experiments, launcher scripts have been developed that create the experiment-specific configuration to be tested. The benchmark applications are HPCC 1.4.2 and Green Graph500 2.1.4, compiled along with OpenMPI 1.6.4 with the Intel Cluster Toolkit 2013.2.146 and Intel Math Kernel Library (MKL) 11.0.2.146. By using the Intel compiler and the MKL BLAS, we generate optimized HPCC and Graph500 binaries that should achieve maximum performance on the target hardware. We note here that even on the AMD platform, this HPCC binary performs significantly better than a GCC 4.7.2 / OpenBLAS 0.2.6 compiled HPL, achieving 120.87GFlops as opposed to only 55.89GFlops with the GCC compiled one for

![](_page_4_Figure_0.png)

Figure 1. Benchmarking workflow - left: without cloud middleware, right: OpenStack IaaS with KVM or XEN hypervisor.

the baseline HPL test on 1 StRemi node.

For the HPCC test, the launcher script calculates the HPC-C/HPL input parameters (N, P, Q) based on the number of nodes in the test and the cluster's specifics - number of cores and RAM size per node, creating a problem size that ensures 80% of total memory occupation. The Graph500 tests' parameters are pre-set to Scale=24 when running with 1 host and Scale=26 for more than 1 host and EdgeFactor=16, Energy time=60(s) in all experiments.

In the OpenStack experiments, the VM configuration *flavor* is created based on the requested number of VMs per host and the known cluster host characteristics - e.g. for a 12-core host with 32GB of RAM, if the desired test configuration is to have 6 VMs, the flavor will be created with 2 cores and 5GB of RAM, with at least 1GB of memory being allocated to the host OS. Throughout all the experiments, the scheduling and network configurations of OpenStack are set by default, as they are recognized as best practices configurations. The FilterScheduler is used to sequentially add VMs to the compute hosts, and in each tested VM configuration the launched VMs are completely mapping the physical resources: each VCPU to a CPU, with 90% of the host's memory being split equally between the VMs. On the networking level the VMs are using the VirtIO network drivers in order to achieve the best possible I/O performance and latency, with each VM's VNIC being bridged to its compute host's NIC, thus the VMs appearing as individual hosts in the configured VLAN.

These configurations and their performance are what any organization deploying this IaaS solution for HPC usage will get in the best possible case, *i.e.* when there is no oversubscribing of resources.

#### *B. Power measurements*

In parallel with the benchmarking process, power measurements were taken in order to quantify the energy efficiency of the tested configurations. The energy consumption data used in our analysis is collected from the Lyon and Reims sites of the Grid'5000 platform where power consumption is measured using wattmeters manufactured by OmegaWatt and respectively Raritan. Power readings are gathered through the Grid'5000 Metrology API and continuously stored in a SQL database. The division of the HPCC and Graph500 benchmark executions into phases (e.g. HPL, DGEMM, CSC, CSR) and correlation with the compute node power consumption, post-processing and statistical analysis is done using the R statistical software. During the power measurements and data analysis the energy used by the cloud controller node is always included. Two stacked power consumption traces for HPCC

![](_page_5_Figure_0.png)

Figure 2. Stacked power traces of baseline, 12 host run (left) and KVM, 12 hosts, 6 VM per host with 1 controller host: t-11 (right), both in Lyon.

and Graph500 are presented respectively in Figures 2 and 3. The thick dashed lines delimit the duration of experiments, while the thinner, dotted lines delimit the phases of each experiment. In the OpenStack test, the power trace for the controller is at the bottom. It can be noticed visually that the HPL execution is the longest, most energy consuming phase of the HPCC benchmark, having the highest peak and average power among all HPCC phases (Figure 2, the last phase). In the GreenGraph500 test, the two Energy loop phases used for energy measurements are very short in comparison with the running time of the whole experiment (Figure 3, two shortest phases).

## V. EXPERIMENTAL RESULTS

This section presents the results obtained, either at the level of pure computing performance (as measured by HPCC's HPL or Graph500 for instance) or at the level of the Green efficiency. In an attempt to improve the readability of the article, we deliberately limit the number of displayed test results to the most significant ones. For instance as regards the HPCC suite, we present here only the performance measures reported for HPL (in GFlops), one of the four STREAM tests (in GB/s) and the RandomAccess benchmark (in GUPS) so as to reflect multiple aspects of the computing system (*e.g.* CPU, memory and interconnect capabilities). The remaining results (DGEMM, PTRANS, FFT and PingPong for HPCC) are of course available on request1. We have then compared the computing performance of the OpenStack Cloud middleware (over the different hypervisors considered) to the baseline environment (corresponding again to classical HPC computing nodes). We use the number of physical nodes as a basis to evaluate the performance reachable by the Cloud environment and the baseline, i.e. OpenStack executions on N nodes with V VMs per nodes are compared to baseline executions on N physical nodes. This allows the clear identification of the overhead induced by the usage of the virtualization platforms on hardware offering the same computation capabilities. In this context, as explained in Section IV, we have evaluated the scalability of each virtualization middleware under the perspective of increasing number of VMs (from 1 to 6) for a fixed number of hosts.

The attentive reader will notice that in very few cases, experimental results are missing. It simply corresponds to situations

![](_page_5_Figure_7.png)

Figure 3. Stacked power traces of baseline, 11 host run (left) and Xen, 11 hosts, 1 VM per host with 1 controller host: stremi-36 (right), both in Reims.

where the deployed VM configuration did not manage to end the benchmarking campaign successfully despite repetitive attempts.

## *A. HPC Performance Results (HPCC and Graph500)*

*1) HPL:* we have first compared the theoretical peak performance Rpeak to the performance of the baseline environment for an increasing number of nodes. The results are displayed in Figure 5. Due to compiling with the Intel suite, we obtain a rather good efficiency on both architectures – around 90% on Intel processors (resp. 50% on AMD processors) for HPL runs involving 12 computing nodes. As mentioned in the section IV-A, it is worth also to note that an execution over the same number of nodes for HPL compiled against the GCC 4.7.2 / OpenBLAS 0.2.6 on AMD machines exhibits a worse efficiency (in this case around 22%), justifying our focus on programs produced by the Intel Cluster Toolkit even in the case of runs over AMD nodes.

![](_page_5_Figure_12.png)

Figure 5. HPL Efficiency of the baseline environment.

Then, Figure 4 compares the HPL performance between OpenStack/Xen, OpenStack/KVM and the baseline. Results are shown for a number of physical hosts ranging from 1 to 12, with a number of VMs per host increasing from 1 and 6. First, we notice that in all cases, the combination OpenStack/Xen performs better than OpenStack/KVM. For Intel processors (top plot), the HPL raw performance in the OpenStack environment is less than 45% of the baseline performance. In the worst case (12 physical hosts with 2 VMs/host), OpenStack/KVM offers even less than 20% percent

<sup>1</sup>A public repository will be configured upon acceptance to host all results.

![](_page_6_Figure_0.png)

Figure 4. High Performance Linpack (HPL) performance for fixed numbers of physical nodes (eventually with increasing numbers of VMs per physical host when running on top of OpenStack).

of the baseline performance. For AMD processors (bottom plot), the HPL performance in the cloud is much closer to the one in the baseline. OpenStack/Xen offers results close to 90% of the baseline in most cases (except for 6 VMs/host) and the OpenStack/KVM performance is between 40% and 70% of the baseline performance. It follows that our experiments emphasize different trends in performance between Intel and AMD processors: the HPL performance with AMD processors on the baseline is only between 50% and 75% of the theoretical Rpeak with our configuration (see Figure 5).

*2) STREAM:* We now present in Figure 6 the results obtained with the STREAM benchmark, which is specifically designed to work with datasets much larger than the available cache on any given system, so that the results are (presumably) indicative of the performance of very large, vector style applications. Globally, our experiments highlight a loss of performance for the order of 40% for Intel processors with OpenStack/Xen (resp. 35% with OpenStack/KVM) compared to baseline results. More surprisingly over AMD processors, the STREAM copy metrics exhibit performance close or even better than the ones obtained in the baseline configuration. The high spatial locality data access patterns of this test allows caching and prefetching mechanisms in the hypervisors to deliver better-than-native performance (behaviour also observed in other studies [22]). Here, the Magny-Cours architecture appears to privilege improved caching strategies for memory operations in the tested versions of Xen and KVM.

*3) RandomAccess:* Random memory access performance often maps directly to application performance and application run time. A small percentage of random memory accesses (cache misses) in an application can significantly affect the overall performance of that application. We thus consider of importance the presentation of the RandomAccess benchmark from the HPCC suite in the OpenStack environment. These results are displayed in Figure 7. In general and on both architectures (Intel and AMD), a performance loss of at least 50% is observed. It can even reach for some configurations 98%. This being said, the results obtained with KVM outperform the ones over Xen. While KVM does not support para-virtualization for CPU, the I/O para-virtualization support for device drivers it features within the so-called VIRTIO subsystem might explain this drastic performances improvement when compared to Xen.

*4) Graph500:* Figure 8 presents the result of the Graph500 benchmark. The reported value is the number of traversed edges which if the performance metric used to rank the machine in the Graph 500 List [14]. We used the CSR implementation which provided the best performance on our configuration among all the other implementations tested. These tests were performed with only 1 VM per host. The results on one physical node show good performance, *i.e.* better than 85% of the baseline, for Xen and KVM hypervisors and for both Intel and AMD architecture. However, when the number of nodes increases, the relative performance drops. For 11 physical hosts, the performance is less than 37% of the baseline performance for the Intel processors, and less than 56% of the baseline for the AMD processors. This is due to the fact that the Graph500 benchmark is communication intensive and that IO performance is strongly affected by the use of VMs [1].

#### *B. Energy-Efficiency Aspects*

*1) Green500:* Figure 9 presents some results of the Green500 benchmark. The baseline results on the Intel platform are only slightly decreasing when scaling to multiple physical nodes, which reflects its high scalability. The energyefficiency of the virtualized environments is slightly improving with an increased number of hosts. This can be explained by the effect of the decreasing influence of the overhead caused by the host running a cloud controller. The performance degradation trend prevails over the diminished overhead effect for

![](_page_7_Figure_0.png)

Figure 6. STREAM copy benchmark results (Sustainable memory bandwidth) in GB/s.

![](_page_7_Figure_2.png)

Figure 7. RandomAccess results (rate of integer random updates of memory) in GUPS.

the settings including more than 8 hosts. The AMD platform in Reims presents worse scalability. The performance-per-Watt (PpW) results decrease with the increasing number of nodes, with the single exception of KVM hypervisors hosting 1 VM per host. On the other hand, the relative overhead is smaller than on the Intel platform. The Xen hypervisor is consistently more energy efficient than its KVM counterpart, however both are much less energy efficient than the baseline configuration. Overall the PpW score decreases with the increase of VMs per host on the AMD platform. KVM is in general more sensitive to the number of hosts per VM, particularly on the

Intel cluster in Lyon, where an increase from 1 to 2 VMs per host leads to an almost twofold decrease in energy efficiency. The further increase of the number of VMs per host increases the efficiency, resulting in the similarity of results for 1 VM per host and 6 VMs per host.

*2) GreenGraph500:* Results for the GreenGraph500 benchmark are presented in Figure 10. The usage of OpenStack has a significant overhead, independently of the type of backend virtualization. The overhead of the CC platform is especially visible with one physical compute node. This is due to the additional node required to run the cloud controller. When the

![](_page_8_Figure_0.png)

Figure 9. PpW metric for the HPL runs as used in the Green500 list.

![](_page_8_Figure_2.png)

Figure 8. Graph 500 harmonic mean results (CSR – Compressed Sparse Row) in GTEPS (109 Traversed edges per second) with 1 VM per physical host.

number of physical nodes increases, the overhead of the cloud controller is reduced, but the energy efficiency of the baseline platform is still considerably better than with OpenStack. This is expected because the raw performance of Graph500 is worse with CC middleware (as shown in Figure 8) but the average power consumption of a computing node is similar whether the benchmark is executed on the bare machine or within a VM. The average power consumption of a computing node is about 200 W for the Lyon nodes and 225 W for the Reims nodes. Better scalability on the Intel platform results in an acceptable decrease of efficiency with the growth of the system size. On the other hand, the AMD platform does not offer a large increase in performance with additional nodes, which results in a rapid decrease of energy efficiency. The differences between the used hypervisors are less significant: the OpenStack/KVM combination slightly outperforms OpenStack/Xen on Intel platform and for the smallest and the largest system size on AMD in Reims, while OpenStack/Xen is better in midsized runs over AMD.

![](_page_8_Figure_6.png)

Figure 10. Green Graph 500 (CSR – Compressed Sparse Row) in GTEPS/W with 1 VM per physical host.

## VI. CONCLUSION

The goal of the present study has been to evaluate the leading open source Cloud IaaS environment OpenStack from an HPC and energy efficiency point of view. In this paper we have described in detail a novel benchmarking methodology that has allowed us to perform experiments by deploying OpenStack on multiple nodes of the Grid'5000 platform on

Table IV. AVERAGE PERFORMANCE DROPS (COMPARED TO BASELINE) ACROSS ALL CONFIGURATIONS AND ARCHITECTURES OBSERVED IN THIS STUDY.

|  |  |  | Avg. Performance drop |  | Avg. Energy-efficiency drop |  |
| --- | --- | --- | --- | --- | --- | --- |
|  | HPL | STREAM | RandomAccess | Graph500 | Green500 | GreenGraph500 |
| OpenStack+Xen | 41.5% | 4.2% | 89.7% | 21.6% | 43.5% | 42% |
| OpenStack+KVM | 58.6% | 7.2% | 67.5% | 23.7% | 61.9% | 40% |

the two leading hardware architectures (AMD and Intel). In particular, we tested the performance impact given by the IaaS solution and its Xen/KVM virtualization backends when running the reference HPCC/HPL and Graph500 benchmarking suites over varying number of physical (up to 12) and virtualized (up to 72) nodes. Our objective was to quantify the overhead induced by the Cloud layer when compared with the baseline configuration that used to operate without any such virtualization interface.

Our findings, summarized in the table IV, show that there is a substantial performance impact introduced by the Cloud middleware layer across the considered hypervisors, which confirms again, if needed, the non-suitability of Cloud environments for distributed large scale HPC workloads. A nonnegligible part of our study includes the energy-efficiency analysis, using the typical metrics employed by the Green500 and GreenGraph500 projects [15], [16]. Indeed, virtualization is also emerging as the prominent approach to reduce the energy consumed by consolidating multiple running VM instances on a single server, thus giving credit towards a Cloudbased approach. Here again, we demonstrate the poor power efficiency of the OpenStack IaaS middleware when facing high-demanding HPC-type applications.

The future work induced by this study includes larger scale experiments over various Cloud environments not yet considered in this study such as vCloud, Eucalyptus, Open-Nebula and Nimbus. Also, an economic analysis of public cloud solutions is currently under investigation that will complement the outcomes of this work. In general, we would like to perform further experimentation on a larger set of applications and machines. Finally, the proposed benchmarks will of course have to be repeated over time in order to evaluate future hardware virtualization ability and new generation of middleware.

Acknowledgments: The experiments presented in this paper were carried out using the Grid'5000 experimental testbed, being developed under the INRIA ALADDIN development action with support from CNRS, RENATER and several Universities as well as other funding bodies (see https://www.grid5000.fr). This work was completed with the support of the INTER/CNRS/11/03/Green@Cloud project and the COST action IC1305.

#### REFERENCES

- [1] M. Guzek, S. Varrette, V. Plugaru, J. E. Sanchez, and P. Bouvry, "A Holistic Model of the Performance and the Energy-Efficiency of Hypervisors in an HPC Environment," in *Proc. of the Intl. Conf. on Energy Efficiency in Large Scale Distributed Systems (EE-LSDS'13)*, ser. LNCS. Vienna, Austria: Springer Verlag, Apr 2013.
- [2] S. Varrette, M. Guzek, V. Plugaru, X. Besseron, and P. Bouvry, "HPC Performance and Energy-Efficiency of Xen, KVM and VMware Hypervisors," in *Proc. of the 25th Symposium on Computer Architecture and High Performance Computing (SBAC-PAD 2013)*. Porto de Galinhas, Brazil: IEEE Computer Society, Oct. 2013.
- [3] "Openstack," http://www.openstack.org/.
- [4] "Grid'5000," [online] http://grid5000.fr.

- [5] M. Armbrust and al., "Above the clouds: A berkeley view of cloud computing," EECS Department, University of California, Berkeley, Tech. Rep., Feb 2009.
- [6] L. M. Vaquero, L. Rodero-Merino, J. Caceres, and M. Lindner, "A break in the clouds: towards a cloud definition," *SIGCOMM Comput. Commun. Rev.*, vol. 39, no. 1, pp. 50–55, Dec. 2008.
- [7] P. Barham, B. Dragovic, K. Fraser, S. Hand, T. Harris, A. Ho, R. Neugebauer, I. Pratt, and A. Warfield, "Xen and the art of virtualization," in *Proceedings of the nineteenth ACM symposium on Operating systems principles*, ser. SOSP '03. New York, NY, USA: ACM, 2003, pp. 164–177.
- [8] A. Kivity and al., "kvm: the Linux virtual machine monitor," in *Ottawa Linux Symposium*, Jul. 2007, pp. 225–230. [Online]. Available: http://www.kernel.org/doc/ols/2007/ols2007v1-pages-225-230.pdf
- [9] X. Wen, G. Gu, Q. Li, Y. Gao, and X. Zhang, "Comparison of opensource cloud management platforms: OpenStack and OpenNebula," in *Fuzzy Systems and Knowledge Discovery (FSKD), 2012 9th International Conference on*, 2012, pp. 2457–2461.
- [10] R. Bolze, F. Cappello, E. Caron, M. Daydé, F. Desprez, E. Jeannot, Y. Jégou, S. Lanteri, J. Leduc, N. Melab, G. Mornet, R. Namyst, P. Primet, B. Quetier, O. Richard, E.-G. Talbi, and I. Touche, "Grid'5000: A large scale and highly reconfigurable experimental grid testbed," *Int. J. High Perform. Comput. Appl.*, vol. 20, no. 4, pp. 481–494, Nov. 2006. [Online]. Available: http://dx.doi.org/10.1177/ 1094342006070078
- [11] E. Jeanvoine, L. Sarzyniec, and L. Nussbaum, "Kadeploy3: Efficient and Scalable Operating System Provisioning," *USENIX ;login:*, vol. 38, no. 1, pp. 38–44, Feb. 2013.
- [12] A. J. Younge, R. Henschel, J. Brown, G. von Laszewski, J. Qiu, and G. C. Fox, "Analysis of virtualization technologies for high performance computing environments," in *The 4th International Conference on Cloud Computing (IEEE CLOUD 2011)*, IEEE. Washington, DC: IEEE, 07/2011 2011, Paper. [Online]. Available: http://www.computer.org/portal/web/csdl/doi/10.1109/CLOUD.2011.29
- [13] P. L. J. J. Dongarra, "Introduction to the hpcchallenge benchmark suite," ICL, Tech. Rep., 2004.
- [14] R. C. Murphy, K. B. Wheeler, B. W. Barrett, and J. A. Ang, "Introducing the graph 500," in *Cray User's Group (CUG)*, may 2010.
- [15] S. Sharma, C.-H. Hsu, and W. chun Feng, "Making a case for a Green500 list," in *Parallel and Distributed Processing Symposium, 2006. IPDPS 2006. 20th International*, 2006, pp. 8 pp.–.
- [16] "Green graph 500." [Online]. Available: http://green.graph500.org
- [17] L. Youseff, R. Wolski, B. Gorda, and C. Krintz, "Evaluating the performance impact of xen on mpi and process execution for hpc systems," in *Proceedings of the 2Nd International Workshop on Virtualization Technology in Distributed Computing*, ser. VTDC '06. Washington, DC, USA: IEEE Computer Society, 2006, pp. 1–.
- [18] A. Gavrilovska et al., "High-Performance Hypervisor Architectures: Virtualization in HPC Systems," in *Proc. of HPCVirt 2007*, Portugal, Mar. 2007.
- [19] P. Luszczek, E. Meek, S. Moore, D. Terpstra, V. M. Weaver, and J. Dongarra, "Evaluation of the HPC Challenge Benchmarks in Virtualized Environments," in *VHPC 2011, 6th Workshop on Virtualization in High-Performance Cloud Computing*, Bordeaux, France, 08/2011 2011.
- [20] K. Ibrahim, S. Hofmeyr, and C. Iancu, "Characterizing the performance of parallel applications on multi-socket virtual machines," in *Cluster, Cloud and Grid Computing (CCGrid), 2011 11th IEEE/ACM International Symposium on*, May 2011, pp. 1–12.
- [21] A. Marathe, D. Lowenthal, B. Rountree, X. Yuan, M. Schulz, and B. de Supinski, "A user perspective of high-performance computing on the cloud," Lawrence Livermore National Laboratory (LLNL), Livermore, CA, Tech. Rep., 2012.
- [22] "HPC Application Performance on ESX 4.1: Stream," http://tinyurl. com/VMWareESX-STREAM-Perf.

