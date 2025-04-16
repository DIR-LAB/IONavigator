# Assessing the Use Cases of Persistent Memory in High-Performance Scientific Computing

Yehonatan Fridman1, 2, Yaniv Snir1, 3, Matan Rusanovsky1, 2, Kfir Zvi1, 2, Harel Levin4, Danny Hendler1, Hagit Attiya5, Gal Oren4, 5

1 Department of Computer Science, Ben-Gurion University of the Negev

2 Israel Atomic Energy Commission

3 Google

4 Scientific Computing Center, Nuclear Research Center – Negev 5 Department of Computer Science, Technion – Israel Institute of Technology

{fridyeh, yanivsn, matanru, zvikf}@post.bgu.ac.il, harellevin@nrcn.org.il, hendlerd@cs.bgu.ac.il, {hagit, galoren}@cs.technion.ac.il

*Abstract*—As the High Performance Computing (HPC) world moves towards the Exa-Scale era, huge amounts of data should be analyzed, manipulated and stored. In the traditional storage/memory hierarchy, each compute node retains its data objects in its local volatile DRAM. Whenever the DRAM's capacity becomes insufficient for storing this data, the computation should either be distributed between several compute nodes, or some portion of these data objects must be stored in a non-volatile block device such as a hard disk drive (HDD) or an SSD storage device. These standard block devices offer large and relatively cheap non-volatile storage, but their access times are orders-ofmagnitude slower than those of DRAM. Optane™ DataCenter Persistent Memory Module (DCPMM) [1], a new technology introduced by Intel, provides non-volatile memory that can be plugged into standard memory bus slots (DDR DIMMs) and therefore be accessed much faster than standard storage devices. In this work, we present and analyze the results of a comprehensive performance assessment of several ways in which DCPMM can 1) replace standard storage devices, and 2) replace or augment DRAM for improving the performance of HPC scientific computations. To achieve this goal, we have configured an HPC system such that DCPMM can service I/O operations of scientific applications, replace standard storage devices and file systems (specifically for diagnostics and checkpoint-restarting), and serve for expanding applications' main memory. We focus on keeping the scientific codes with as few changes as possible, while allowing them to access the NVM transparently as if they access persistent storage. Our results show that DCPMM allows scientific applications to fully utilize nodes' locality by providing them with sufficiently-large main memory. Moreover, it can also be used for providing a high-performance replacement for persistent storage. Thus, the usage of DCPMM has the potential of replacing standard HDD and SSD storage devices in HPC architectures and enabling a more efficient platform for modern supercomputing applications.

The source code used by this work, as well as the benchmarks and other relevant sources, are available at: https://github.com/ Scientific-Computing-Lab-NRCN/StoringStorage.

*Index Terms*—Non-Volatile RAM, Optane™ DCPMM, NAS Parallel Benchmark, PolyBench, FIO, PMFS, SplitFS, NOVA, ext4-dax, xfs, DAOS, DMTCP, SCR

## I. INTRODUCTION

Modern scientific research and advanced industries make massive usage of *High Performance Computing* systems. This makes these systems a critical resource in both private and public sectors, supporting compute-intensive calculations that are otherwise impossible to perform [2]. Indeed, many recent achievements in Physics, Chemistry, Engineering, Biology, Medicine, Computer Science and more, rely on computations performed by HPC systems [3]. As the demand for larger calculations and simulations increases, huge amounts of data should be analyzed, manipulated and stored [4].

In the traditional memory management approach, each compute node stores its data objects in its local volatile DRAM [5]. Whenever the memory requirements of the application exceed the node's DRAM capacity, the computation should either be 1) distributed, along with the node's data objects, between several compute nodes, or 2) accommodated by the node by relying on the operating system's virtual memory support, for storing portions of the node's data objects in storage devices attached to it using paging [5]. Unfortunately, the gap between the speeds of DRAM and standard block storage devices is about three orders of magnitude [6]. As computations grow in scale, especially in the exa-scale era, this performance gap becomes intolerable [7]. Moving data between DRAM and a block device is costly in terms of application runtime [5]. On the other hand, DRAM is much more expensive than standard storage devices [6] and its power consumption is higher, due to the cost of keeping it fresh and alive [8]. Thus, building cost-effective systems with large memory and storage spaces that are resilient, fast and power-efficient is a major challenge faced by the HPC community [9], [10].

Another challenge is that as HPC architectures become more complex, with larger numbers of compute nodes, the fault rates of large-scale computations increase [4]. At the same time, the runtime penalty incurred by each application crash becomes more and more expensive. Consequently, in addition to the constant improvements in the sustainability of HPC clusters, the resilience of scientific applications becomes an important requirement. In traditional HPC memory arrangements, whereas most of the frequently-accessed data is stored in volatile DRAM, various techniques are used to save important data to persistent storage so that it will be available for recovery after an application or system failure [11], [12]. The most common way of persisting such important data is by storing *check-points* along the program's execution. The frequency of check-pointing is determined according to the probability of crashes in the system and the nature of the algorithm. However, as mentioned above, moving data from the DRAM to storage takes a significant amount of time.

A new technology introduced by Intel, called Optane™ DataCenter Persistent Memory Module (DCPMM), provides non-volatile memory (NVM) that can be accessed much faster than standard storage devices and is plugged to standard memory bus slots (DDR DIMM). Moreover, unlike contemporary storage devices that can only be accessed in block granularity, Optane™ DCPMM memory is byte addressable and can thus be accessed by applications using regular loads and stores. Due to these advantages, Optane™ DCPMM offers a new tier in the memory-storage hierarchy, which fits perfectly in the gap between memory (registers, cache and DRAM) and storage (SSDs and HDDs).

## *Contribution*

In this work, we present a comprehensive performance assessment of storageless persistent-memory supercomputing configurations. We test several such configurations, in which Intel Optane™ DCPMM and its novel utilities 1) fill the gap between standard storage devices and file systems (especially for diagnostics and checkpoint-restarting), and 2) serve as an expansion of the memory hierarchy that can be used directly by applications, partially replacing the need for expensive paging. Unlike previous research in this field, we focus on scientific benchmarks that are often used for evaluating the performance of parallel supercomputers. We experiment with representative memory and storage usage scenarios scientific applications that run on HPC systems, in order to assess the extent to which NVM can increase productivity for scientific computing. Specifically, we focus on the following three NVM use cases: (1) Using NVM to expand a node's main memory; (2) Using NVM as a fast local storage area; (3) Using a combination of NVM and DRAM for implementing a fast internal and external checkpoint-restart mechanism.

We evaluate the potential benefits of DCPMM for HPC scientific computing by using widely-used parallel benchmarks, such as NPB and PolyBench (see Section III).

Our results show that Optane™ DCPMM allows scientific applications to better utilize nodes' locality. It is able to greatly enlarge a node's main memory and can be used also for storing high performance file systems. In addition, it can be used for enhanced checkpoint-restart support. Viewed collectively, these results indicate that DCPMM opens up opportunities for new exa-scale NVM-supported supercomputers. The reliance of these new HPC architectures on standard storage devices (HDDs and SSDs) for scientific computing can be greatly reduced, allowing better performance.

## *Related Work*

Optane™ DCPMM [1] is a relatively new hardware, still not fully present in any supercomputer worldwide. Thus, it was subjected so far only to limited examination on scientific workloads. Deployment of Optane™ DCPMM for highperformance scientific applications was evaluated [13], [14], [15], measuring outright performance, efficiency and usability for both its Memory and App Direct modes. However, these works do not assess the feasibility of eliminating the intrinsic need for standard storage altogether, including for local and distributed diagnostics and checkpoint-restart flows, as a complete solution.

Extending node main memory was tested in several benchmarks and production legacy codes [16], [17], [18], [19], [19], [20], measuring the extent of performance degradation for scientific workflows in comparison to DRAM-only usage. Previous results for local and distributed persistent memory file systems with NVM are also promising for several real-world applications, exemplifying significant improvements over current state-of-the-art NVMe SSD storage. However, most of the benchmarks employed [21], [22], [23], [24], [25] are not scientific workflows or are not based on common stressors for scientific patterns in supercomputing such as BTIO [26] with all of its variants under MPI. Furthermore, these works do not compare local and distributed storage over RDMA, and they also do not compare to common storage devices such as HDD or SATA-SSD, which are still very common in largescale distributed storage systems. The same holds for previous evaluations of the use case of failure recovery, either internal or external [27], [28], [29], via diagnostic to DCPMM and restart from DRAM.

#### *Organization*

The rest of the paper is organized as follows. Section II presents the Optane™ DCPMM and the hardware setting we used for this work. In Sections III and IV, we describe the well-known NPB and PolyBench scientific application benchmarks and use them for evaluating the performance gained by using NVM as a main memory expansion in comparison to using paging. In Section V, we evaluate the usage of Optane™ DCPMM as a persistent memory storage, using representative local Persistent Memory File Systems (PMFSs). We compare the performance of this solution with that of local SATA SSD using the BTIO specialized benchmark for I/O. Finally, Section VI presents Optane™ DCPMM as a fast storage for internal (SCR) and external (DMTCP) Checkpoint/Restart storage over local PMFS using the BT solver (from the NPB suite) and compare its performance to that of local SATA SSD. We conclude, in Section VII, with a review of Optane™ DCPMM's current functionalities and

| #Sockets | 2 |
| --- | --- |
| CPU Spec. | 10 Cores × Intel(R) Xeon(R) Gold 5215 CPU @ 2.50GHz (per socket) |
| L1 Cache | 32KB i-Cache |
|  | 32KB d-Cache (per core) |
| L2 Cache | 1024KB (per core) |
| L3 Cache | 14080KB (shared, per socket) |
| DRAM Spec. | 16GB DDR4 DRAM 2933 MT/s |
| Total DRAM | 192GB [(2 sockets)× |
|  | (6 channels)×16GB] |
| NVM Spec. | 256GB Intel Optane™ DCPMM |
|  | 2666 MT/s Apache Pass |
| Total NVM | 1024GB [(2 sockets)× |
|  | (2 channels)×256GB] |
| SSD Spec. | 240GB 6GB/s Intel SATA 2.5” |
|  | SSD |
| Network | 56Gb/s Mellanox Infiniband FDR |
| Hyper-Threading | disabled |
| OS | Linux CentOS 7.9, Kernel 4.13.0 |

![](_page_2_Figure_1.png)

(b) DCPMM population configuration of a node, with two sockets (SO) connected via an interconnect, used in our experimental environment. Each CPU unit has two memory controllers (MC), each providing three memory channels (CH) and each memory channel contains two DIMM slots. D (in red) denotes DCPMMs, R (in blue) denotes DRAMs (i.e RDIMMs), and white denotes vacancy. Red slots refer to 256GB Optane™ DCPMMs, and blue slots refer to 16GB DDR4 RAM DIMMs.

(a) Experimental environment specifications.

Fig. 1: Experimental environment specifications and DCPMM population.

future potential for scientific computations in the new exascale supercomputing era.

#### II. OPTANE™ DCPMM AND HARDWARE SETTING

Traditional architectures [30] use non-volatile memory only as Double Data Rate (DDR) Dual In-line Memory Modules (DIMMs), accessed through standard DDR cards using an ancillary battery. Upon a power failure, the data is washed to a non-volatile disk. Intel Optane™ DCPMM uses the same memory connection as DDR DIMMs, and therefore Xeon™ processors can use it as a *standard byte-addressable memory*, in addition to using it as non-volatile memory. Each DCPMM can be configured in one of two modes:

1) *Memory Mode* (also called *Memory-side Cache*, *2-Level-Memory* or *IMDT*): This mode uses the DCPMM as a pool of volatile memory. When DCPMM is configured in this way, the system sees it as its exclusive memory and the DDR serves as the *cache* for the Non-volatile DIMM (NVDIMM). This approach is beneficial when a relatively cheap memory expansion is required, because NVDIMM pieces are cheaper than standard DDR pieces and have a much larger volume. A significant advantage of this mode is that it is very easy to adapt the DCPMM to the system (almost "Plug and Play"). However, this mode has several disadvantages in using nonuniform memory access (NUMA) codes when running different applications on the cores, since localization is not perfect and DDR cannot really be used as sophisticated cache [31]. In addition, performance does not scale in this mode as well as with DDR, although when the application does not produce many page faults, performance is expected to be close to that of standard RAM [31].

2) *App Direct* (also called *1-Level-Memory*): This mode uses the persistent memory (PM) directly from the application, so that the DDR is used as volatile cache memory while the NVDIMM is used as RAM. The NVDIMM is directly connected to the CPU (via the Memory Bus), and can thus be accessed significantly faster than standard storage. The difference between NVDIMM and NVMe SSD devices (e.g. Intel Optane™ SSD) is that the latter are connected via the PCIe, which adds additional overhead. Moreover, in this mode, *block I/O* can be used as with standard storage, but much faster since the connection is done via the memory bus. However, in order to use the NVDIMM as NVM and access it at the *byte-level* using loads/stores, it has to be mapped to virtual memory via Direct Access (DAX) from the application. The drawback is that direct access requires extra programming effort. In NUMA architectures, Device DAX can be used in App Direct mode to gain access to the images of both NUMA nodes so that the application is able to choose which memory to use for normal allocations. In this work, we chose not to use this feature in order to keep the configuration of the nodes as close to the standard as possible.

The *Persistent Memory Development Kit* (PMDK) [32] is a collection of libraries and tools created by Intel for application developers and system administrators to simplify access and management of persistent memory devices. It consists of volatile libraries (e.g. libmemkind and libvmem) that provide control of memory characteristics, as well as of persistent libraries (e.g. libpmem and libpmemobj), which help applications maintain the consistency of data structures in the presence of failures. These libraries provide new semantics that require extensive application modifications, and in some cases even necessitates building the applications from the ground up [32]. In this work, we do not use PMDK libraries or any other extensive inner-code modifications, but rather employ a transparent approach in which scientific applications access NVM mainly using persistent memory file systems and conventional tools for HPC Checkpoint/Restart.

Our experimental environment consists of a dual-socket server (see specifications in Fig. 1a). The DCPMM population configuration is 2-1-1 (see Fig. 1b). When using NVM as a node's memory expansion, we applied the Optane™ DCPMM Memory mode, while in the rest of the paper, we applied the App Direct mode. We note that it is possible to configure

![](_page_3_Figure_0.png)

Fig. 2: FIO benchmark results, tested on the Optane™ DCPMM and SATA-SSD of our experimental environment.

DCPMM in Mixed Mode, where a percentage of the hardware capacity is used in Memory Mode and the remainder in App Direct Mode.

## *Optane™ DCPMM as a Persistent Storage - FIO Benchmark*

The Flexible I/O Tester (FIO) [33] is a versatile storage benchmark tool that is used both for benchmarking and stress/hardware verification. Fig. 2 shows a comparison between the bandwidth of basic read/write file operations in FIO on Optane™ DCPMM and SATA-SSD. We run FIO v3.7 using the *sync* ioengine, with a 512MB file size per thread and 8KB read or write block size. For write workloads, we issue an *fsync()* after each 8KB are written. Each workload runs for 30 seconds, and the number of threads vary from one to eight, with each thread accessing a different file. Like Izraelevitz et al. [34, Chapter 5.2], we evaluate the performances using various file systems: xfs, ext4, ext4-dax, NOVA [35]. We note that file systems which enable DAX cannot run on SATA-SSD, hence only the non-DAX file systems were tested on the SATA-SSD device. Most of the bandwidth trends increase with the number of threads, since the application does not fully exploit the available bandwidth. The trends of our results differ somewhat from Izraelevitz's results, apparently due to differences in system configuration and memory population. Nevertheless, similarly to [34], the results demonstrate that Optane™ DCPMM is superior to SSD with regards to *basic I/O operations*. The rest of this work compares the performance of *scientific HPC benchmarks*, described next, on Optane™ DCPMM and on SSD.

#### III. SCIENTIFIC COMPUTING BENCHMARKS

The NPB [36] and PolyBench 4.2.1 beta [37] parallel benchmarks are used in this work in order to evaluate how scientific applications perform on storage-free setting and to establish a comparable performance metric. PolyBench was adjusted to the present memory hierarchy, so that the DRAM acts as a cache to the DCPMM. All of our benchmarks were executed using a single computation node (see the specs in Section II).

The Numerical Aerodynamics Simulations (NAS) Parallel Benchmarks set is a well-known suite of applications, developed by NASA, designed to evaluate the performance of highperformance computers. Originally, NAS Parallel Benchmarks (NPB) consisted of five parallel kernels: Integer Sort (IS), Embarrassingly Parallel (EP), Conjugate Gradient (CG), Multi-Grid (MG) and Fourier Transform (FT); and three pseudoapplications: Block Tri-diagonal solver (BT), Scalar Pentadiagonal solver (SP) and Lower-Upper Gauss-Seidel solver (LU) [38]. Later, a few other representative HPC applications were added to the benchmark suite, e.g., Unstructured Adaptive mesh (UA), BT using parallel I/O techniques (BTIO). Problem sizes in NPB are predefined and classified as follows: small size (class S), 90's workstation size (class W), standard sizes with ×4 size increase between the following classes (classes A,B,C), and large sizes with ×16 size increase (classes D,E,F).

A prominent benchmark is BT, simulating a computational fluid dynamics application. Its solution is derived by solving three uncoupled systems of equations: first at the direction of x, then at the direction of y, and finally at the direction of z. These systems are composed of 5 × 5 block matrices given in a block-tridiagonal form. We chose to concentrate on this benchmark throughout our work. We also used a derivative of BT, BTIO, which benchmarks the performance of PnetCDF and MPI-IO methods for the I/O pattern used by the NPB suite. It measures the communication speeds for parallel intensive I/O, and is used for evaluating storage performance.

It is not easy to modify the predefined problem sizes in NPB. As can be seen in Fig.3, the differences between them are too coarse around the capacity of DRAM that we use in a node (192GB). To evaluate the memory expansion of Optane™ DCPMM, a more refined examination of the hardware behavior is needed around the point where DRAM is fully occupied. We use the PolyBench suite for this purpose, since its granularity can be tuned in finer manner than NPB. PolyBench [37], [39] is a collection of 30 representative HPC applications from various domains, e.g., linear algebra, image processing, physics simulation. PolyBench aims to make the execution of the kernels as uniform as possible, using benchmarks that contain static control parts. Kernel setting is done by a single file that is tuned at compile time. This file executes supplementary operations such as cache flushing before the kernels are executed, and can carry out real-time scheduling to prevent operating-system interference.

PolyBench 4.2.1 has five predefined problem sizes: less than 16KB of memory—may fit within L1 (MINI), around

![](_page_4_Figure_0.png)

(a) DCPMM Expansion (Optane™ DCPMM in Memory Mode)

(b) Memory Swap (SATA-SSD swap partition)

![](_page_4_Figure_3.png)

![](_page_4_Figure_4.png)

(a) DCPMM Expansion (Optane™ DCPMM in Memory Mode)

## (b) Memory Swap (SATA-SSD swap partition)

Fig. 4: Floating-point Operation Throughput of PolyBench Benchmarks

128KB of memory—may fit within L1 (SMALL), around 1MB of memory—would not fit in L1, but may fit within L2 (MEDIUM), around 25MB of memory—would not fit in L3 (LARGE), and finally, around 120MB of memory (EX-TRALARGE). Although PolyBench was designed to evaluate the performance of HPC applications on small predefined problem sizes, these problem sizes can be easily modified. In order to further test the performance of HPC applications coupled with non-volatile memory, we modified the benchmarks so that the behavior of the execution is examined relative to the memory consumption in a finer granularity, specifically around the DRAM capacity which is 96GB in a socket of our setting (we bind PolyBench to memory resources of one socket). Most of the benchmarks in the same category are computationally comparable (e.g jacobi-1d versus jacobi-2d). Therefore, we chose representative benchmarks in each category (except for *Medley*, considered redundant in this context), while focusing especially on benchmarks from *Linear-Algebra* and *Stencils*. When technically possible, for example in stencils computations, we executed the benchmarks for a relatively small number of time steps, not necessarily reaching convergence.

#### IV. DCPMM AS EXTENDED VIRTUAL MEMORY

A big limitation of traditional HPC is the main memory capacity, i.e., the size of DRAM that is installed in a compute node is limited due to hardware, software and economic factors. In order to overcome DRAM limits some HPC applications distribute their memory (and computations) between several compute nodes (e.g. using MPI [40]), or use the virtual memory mechanism, which swaps the contents to or from the primary memory with the secondary storage. Both solutions have disadvantages: distributing memory among multiple nodes comes with programming efforts but mainly large overheads of communication between the nodes; and swapping data to a secondary memory dramatically decreases performances due to extremely high access time to the secondary storage (compared to DRAM) and to kernel management overheads. Using NVM as an extension to the primary memory creates a solution to the DRAM limit problem, which is transparent to the operating system and to the user.

When configuring Optane™ DCPMM in Memory Mode as primary memory extension on a node, DRAM DIMMs are logically viewed as L4 cache and not as system memory. Therefore the total system memory as seen by the operating

![](_page_5_Figure_0.png)

![](_page_5_Figure_1.png)

Fig. 5: Memory Bandwidth of BTIO Benchmark with the MPI-IO method

system is based on the total capacity of the installed DCPMM devices [41]. To evaluate the usage of DCPMM devices as primary memory expansion, NPB and PolyBench benchmarks were executed on a single node of our experimental environment (Section II), with all its Optane™ DCPMMs configured in Memory Mode. PolyBench benchmarks were executed on one core with the memory resources available in one socket (96GB DRAM and 512GB Optane™ DCPMM). NPB benchmarks were executed with 16 processes using the entire memory resources of a node (192GB DRAM and 1024GB Optane™ DCPMM). To compare these results with a traditional solution, these benchmarks were also executed on a configuration without Optane™ DCPMMs, but with memory swapping to a SATA-SSD device. As can be seen in Figs. 3 and 4, the performances of scientific applications are almost the same before passing the DRAM limit (marked in gray line). After passing the DRAM limit, however, they decrease only by a factor of 2-3 on average when using Optane™ DCP-MMs for primary memory extension, whereas they deteriorate by 2-3 orders of magnitude when using memory swapping to SSD. This serves as evidence to the dramatic improvements in performance of scientific applications that Optane™ DCPMMs offers for large workloads.

(c) BTIO MPI Collective I/O (Read)

# V. DCPMM AS PERSISTENT-MEMORY FOR LOCAL AND DISTRIBUTED FILE SYSTEMS

Persistent Memory File Systems (PMFSs) include both local and distributed file systems. Local persistent file systems include ext4, xfs (for Linux-based systems), and NTFS (for Windows-based systems). They support a special mode called Direct Access (DAX) that enables memory mapping directly from the NVM to the application memory space. This bypasses the kernel, page cache, I/O subsystem, avoids interrupts and context switching, and allows the application to perform byteaddressable load/store memory operations [42].

Several other file systems have been developed with performance and other guarantees (e.g. consistency, atomicity, fault tolerance) in mind. These include NOVA [35] and SplitFS [43], both providing POSIX compliant interfaces that support legacy scientific applications. NOVA is designed to maximize performance on hybrid memory (combining DRAM and NVM) systems while providing strong consistency guarantees. It is log-structured, and as such, it exploits the fast random access that NVMs provide, by storing the logs in the NVM and the indexes in the DRAM to allow fast search operations. *SplitFS* presents a split of responsibilities between

![](_page_6_Figure_0.png)

(a) Crash-free BT on different non-volatile hardware (b) Breakdown of recovery, checkpoint and compute time per iteration in a single crash and recovery run of BT. (c) Checkpoint size of BT with SCR and DMTCP

Fig. 6: Comparison of SCR and DMTCP on the BT benchmark on different non-volatile hardware settings.

a user-space library file system and an existing kernel PMFS. The user-space library file system handles data operations via POSIX calls interception, memory-mapping the underlying files, and serving the read and overwrites using processors loads and stores. The PM file system (ext4-dax) handles metadata operations.

While these local PMFSs are good choices for single-node workloads, scientific computing applications usually require a distributed PMFS that operates on several nodes. Distributed PMFSs control how data is stored and retrieved from NVM when accessed by more than one node, using communication, such as Ethernet and RDMA.

Nowadays, most supercomputers contain disk-less nodes with a centralized storage, that all applications access and communicate with. This makes the formation of a distributed PMFS using distributed NVM units a great challenge. Octopus [44], Assise [45] and DAOS [46], [47] are the most contemporary and promising DFSs for this setting.

*Octopus* closely couples NVM and RDMA in order to reduce memory copying overhead. It presents a directlyaccessed shared persistent memory pool setup in every server, with the shared memory mechanism of Linux. This allows data fetching from clients, and data pushing to clients based on server and network loads. Octopus is incompatible with Intel's Optane™ DCPMM since it manages its storage space on an emulated persistent memory of Linux in each server.

*Assise* is built on the local file system Strata [48], originally developed as a cross-media file system. Its main goal is to support work over several types of storage media (RAM, SSD, Disk), leveraging the strengths of one storage media to compensate for weaknesses of another. Assise extended this work to provide a DFS based on a persistent, replicated coherence protocol. This protocol manages client-local Persistent-Memory as a linearizable and crash-recoverable cache between applications and slower (and possible remote) storage. When trying to use Assise, we discovered several issues. First, its system call interception mechanism lacks support for many necessary system calls. As a result, it is not possible to run even simple GNU programs such as *touch* or rm [49]. Second, Assise is incompatible with MPI implementations such as OpenMPI since the *execve* system call is not yet supported [50]. Finally, DMTCP, which is widely used for checkpointing scientific applications cannot run with Assise since the system call interception mechanism of Assise collides with that of DMTCP's, resulting in an infinite loop. Unlike Octopus and Assise, state-of-the-art *DAOS* is designed from the ground up to support Storage Class Memory and NVMe storage in user space. In this new storage paradigm, POSIX is no longer the foundation for new data models. Its advanced storage API enables the native support of structured, semi-structured, and unstructured data models, overcoming the limitations of traditional POSIX based parallel file-systems [46]. At the same time, DAOS provides POSIX access for legacy applications, as well as direct MPI-IO and HDF5 support. The DAOS File System is implemented in the *libdfs* library, and allows a DAOS container to be accessed as a hierarchical POSIX namespace. In addition, there is a FUSE daemon (optionally with an interception library, *libioil*), which addresses some of the FUSE performance bottlenecks. This delivers full OS bypass for POSIX read/write operations, and exposes the POSIX emulation transparently, without any modifications [46], [51].

Fig. 5 focuses on the BTIO benchmark with MPI-IO method to evaluate the I/O performances of some PMFSs on the Optane™ DCPMM in App Direct mode, in comparison to I/O performed on a SATA-SSD device. BTIO was executed with 4 processes, and was modified to execute a file sync (with MPI *File sync*) after every write, to ensure the immediate transition of data to the Optane™ DCPMM and SATA-SSD devices. As can be seen, using Optane™ DCPMM with various PMFSs can dramatically increase I/O operations in scientific computing applications. The increase seems to be more significant on read workloads (up to ×10 speedup), compared to the increase of write workloads performances (up to ×3-×3.5).

## VI. DCPMM AS CHECKPOINT/RESTART (C/R) STORAGE

Many large scale, and especially exa-scale scientific simulations, where performances is top priority, run on HPC platforms with millions of components. These components are extremely vulnerable to failures, which leads to the loss of simulation results as well as a waste of highly-priced resources (including power and actual computation time for other applications). This raises the need for a scalable and reliable fault tolerance mechanism that supports large scale scientific codes.

In *explicit C/R*, in order to successfully checkpoint and restart a program from a valid state, the program has to store (and restore from) the whole required computational state. For scientific simulations, this usually consist of the data and the current time-step. The state is saved and restored manually within the program, and it is the responsibility of the programmer to understand what information is necessary and sufficient for correct recovery. If the state is represented compactly, i.e., the checkpoint file contains exactly what is required for a correct restart to be carried out, the C/R overhead might stay comparably low. *Scalable Check-point/Restart (SCR)* is state-of-the-art library [11], [52], [53], developed by Lawrence Livermore National Laboratory (LLNL), which supports scalable explicit C/R. SCR deploys multilevel checkpointing [11], which supports both (1) frequent, fast, but more volatile check-points to the node local RAM/Disk that may be used to recover from software faults, as well as (2) less frequent, slower but persistent check-points to the DFS that can withstand substantial software failures.

In *transparent C/R* the state of the program is saved without any knowledge of the application or intervention from the programmer. A possible implementation of such approach might be based on checkpointing in the userspace by catching and wrapping any needed system calls, in order to continually track the state of the program application. Additionally, since transparent C/R is oblivious to program behavior, each call that involves any external resources outside the process (e.g., network or storage), has to be documented via non-volatile log file in order to replay them in case of a failure. Capturing system calls and maintaining a log file inflicts a measurable performance penalty for the application. The *Distributed Multi-threaded CheckPointing* (DMTCP) [54] library enables transparent C/R of a single-host, parallel or distributed computation, using a preloaded shared library that wraps system calls. DMTCP does so without any requirement for modifications to the source code or the operating system, supporting a variety of HPC languages and infrastructures, including MPI and OpenMP [55], and InfiniBand [56].

Restoring the state of the program requires writing to and reading from non-volatile hardware. Traditionally, programs and in particular HPC simulations carried out their C/R functionality in conventional storage (HDD and SSDs). This imposed a significant running-time penalty. Since NVM offers a non-volatile 'storage' option with improved read and write stats, it is interesting to evaluate the performance gap between it and traditional storage. In order to test the C/R performance on the different non-volatile hardware, we use the BT benchmark from the NAS Parallel Benchmarks suite [36]. Note that the scientific application evaluated in Section IV involves only writes to the NVM, while the following application consists of both writes to and reads from the NVM.

Fig. 6a-6c evaluate the cost of storing checkpoints by presenting the performance of three algorithms: Original BT (without check-pointing); BT with SCR; and BT with DMTCP, on the problem class D (matrix of size 408 × 408 × 408), on two non-volatile hardware components: SSD and DCPMM (as described in Section II). Problem class D was chosen as it is the largest problem that fits into memory.

Similarly to Maronas et al. [ ˜ 57], BT's MPI implementation was expanded to support scalable checkpoint recovery (SCR). That is, at the end of each iteration, the solver inner state is checkpointed. Upon recovery after a failure, the most recent valid checkpoint is loaded. Due to the layered nature of SCR, our implementation flushes the checkpoint from the cache to the persistent memory, at the end of each iteration. While DMTCP checkpoints are external to the process, for a fair comparison, we modified BT to initiate checkpoints at the end of each iteration.

Fig. 6b evaluates the cost of writes and reads to and from NVM and SSD in a scientific application. It measures the crash and recovery performance of BT with SCR and BT with DMTCP. Values in Fig. 6b are normalized to a single iteration.

Fig. 6a shows that in both scenarios, as the number of processes is close to 1, DMTCP implementations perform better than their SCR equivalents. A 15% rise is seen in NVM and a 27% increase in SSD in the total run time when running crash-free with a single process. We can see that the trend changes beyond 4 processes: as the number of processes increases, SCR performs better. SCR shows a 42.2% decrease in run time on NVM and a decrease of 39.1% on SSD when running with 16 processes. This can be explained by higher overhead times that SCR suffers from, when running as a single process. DMTCP scaled worse beyond 4 processes, leading to a worse processing time as the number of processes grows. Overall, both algorithms perform better on NVRAM than on SSD as it performs x1.02-x2.49, 1.12-2.62x faster on BT-DMTCP and on BT-SCR respectively.

In the settings of a single crash and recovery, BT-SCR shows a smaller recovery overhead than the recovery time of BT-DMTCP regardless of the number of processes. As the number of processes grows, the recovery overhead drops. BT-SCR scales better as the recovery time decreases. Specifically, the recovery in NVM and SSD seems equal on BT-SCR as the read operation is very short and therefore the difference seems insignificant. BT-DMTCP shows an improvement in up to 9 processes, where beyond 16 processes there is a slight increase in recovery duration of ×1.36 and ×1.1 for NVRAM and SSD respectively. This increase can be explained by the fact that the computation spans on two sockets, therefore it requires slower communication. Surprisingly, in the case of BT-DMTCP, the recovery performance on NVRAM is slightly worse than the performance on SSD (between ×1.5-×2).

The checkpoint duration demonstrates several trends. In most scenarios, both algorithms checkpoints are faster on NVRAM than on SSD. BT-SCR shows shorter checkpoint durations over NVRAM, compared to SSD. As the number of processes increases to 9 threads, BT-SCR-NVM's checkpoint duration speeds up by ×3.11 compared to a serial run, whereas with 16 processes it reduces to a speed up of ×2.28. However, BT-SCR-SSD shows a mild speed-up from a serial run to 4 processes (×1.19) with a slight decrease beyond 4 processes to ×1.06 (16 processes). BT-DMTCP-NVRAM, shows a similar pattern as BT-SCR on top of NVRAM, with a checkpoint speed-up of ×2.8 to 9 processes with a slow-down by ×2.12 with 16 processes compared to a serial run. BT-DMTCP-SSD however, shows a slow-down of ×0.25 of the checkpoint duration from 1 process to 4 processes whereas beyond 4 processes there isn't any further slow-down compared to a serial run. As expected, the computation time decreases as the number of processes grows, and remains oblivious to the hardware on which the checkpoint is written.

Fig. 6c demonstrates the differences between conducting explicit C/R and implicit C/R in terms of checkpoint size in a scientific application, by measuring the checkpoint size of BT with SCR and BT with DMTCP. SCR checkpoints are smaller by 62%-63%. In addition, there is a steeper increase in DMTCP checkpoints size as the checkpoint size grows from 23.64GiB (1 process) to 26.97GiB (16 processes). On the other hand, the checkpoints size of SCR, which has been developed to scale well, shows a gentle growth in size – 8.77GiB (1 process) to 9.31GiB (16 processes).

#### VII. CONCLUSIONS AND FUTURE WORK

Future exascale supercomputing systems will incorporate non-volatile memories. An example for such an HPC system that includes Intel DCPMM, is Aurora [58]. These new types of non-volatile memories offer simultaneously an ultra-fast storage and a relatively comparable main memory extension, supposedly cheaper than DRAM, with much larger volume per single DIMM. By that, these hardware represent a fundamental change, not only to the decades-long memory hierarchy paradigm, but also to high-performance applications and their use-cases. Since scientific HPC applications naturally starve for more byte-addressable memory, as well as for much faster storage, there is a need to understand if and how these applications can optimally utilize non-volatile memory for their benefit. This paper investigates whether non-volatile memory can constitute a much faster replacement for standard storage, or a cost-effective alternative for DRAM with regard to highperformance scientific computations. We carefully study usecases of the non-volatile memory in current HPC settings, and examine representative parallel scientific benchmarks. We evaluate memory expansion, persistent memory storage, and explicit/transparent check-point restart configurations. We seek to minimize changes to the source codes, with the support of an appropriate FS over the NVM.

Our results show that in all of the suggested tasks, DCPMM exhibits outstanding performances. Specifically, DCPMM allows to expand the byte-addressable memory at the expense of only a few factors of cost; it drastically improves access times to persisted storage in comparison with SSD, under various file systems; and it even facilitated C/R greatly.

As mentioned in Section V, scientific computing relies on DFSs when workloads are executed across multiple nodes. For future work, we plan to set up a multi-node environment (consisting of at least two nodes) and to explore the readiness of DAOS to support Optane™ DCPMM as a distributed storage. Once there are changes in Assise to improve its system call interception mechanism and to make it compatible with MPI implementations, we will be able to evaluate Assise and to compare it to DAOS in the context of scientific distributed computing.

We conclude that next generation supercomputing systems might be able to avoid the use of standard storage completely and to adopt non-volatile memories for better performance as well as higher fault tolerance. Non-volatile memory should not be overlooked. Moreover, there are still many possibilities to exploit its full potential in future software, specifically, for scientific simulations, especially in the presence of new, more advanced technology [59].

## ACKNOWLEDGMENTS

This work was supported by Pazy grant 226/20 and the Lynn and William Frankel Center for Computer Science. Computational support was provided by the NegevHPC project [60]. The authors would like to thank Israel Hen and Emil Malka for their hardware support.

#### REFERENCES

- 1 Liu, H.-K. *et al.*, "A survey of non-volatile main memory technologies: State-of-the-arts, practices, and future directions," *Journal of Computer Science and Technology*, vol. 36, no. 1, pp. 4–32, 2021.
- 2 Hager, G. *et al.*, *Introduction to high performance computing for scientists and engineers*. CRC Press, 2010.
- 3 Kaufmann, W. J. *et al.*, *Supercomputing and the Transformation of Science*. WH Freeman & Co., 1992.
- 4 Snir, M. *et al.*, "Addressing failures in exascale computing," *The International Journal of High Performance Computing Applications*, vol. 28, no. 2, pp. 129–173, 2014.
- 5 Jacob, B. *et al.*, *Memory systems: cache, DRAM, disk*. Morgan Kaufmann, 2010.
- 6 Luttgau, J. ¨ *et al.*, "Survey of storage systems for high-performance computing," *Supercomputing Frontiers and Innovations*, vol. 5, no. 1, pp. 31–58, 2018.
- 7 Harrod, W., "A journey to exascale computing," in *2012 SC Companion: High Performance Computing, Networking Storage and Analysis*. IEEE, 2012, pp. 1702–1730.
- 8 Fan, X. *et al.*, "Memory controller policies for dram power management," in *ISLPED'01: Proceedings of the 2001 International Symposium on Low Power Electronics and Design (IEEE Cat. No. 01TH8581)*. IEEE, 2001, pp. 129–134.
- 9 Oren, G. *et al.*, "Memory-aware management for heterogeneous main memory using an optimization of the aging paging algorithm," in *2016 45th International Conference on Parallel Processing Workshops (ICPPW)*. IEEE, 2016, pp. 98–105.
- 10 Bergman, K. *et al.*, "Exascale computing study: Technology challenges in achieving exascale systems," *Defense Advanced Research Projects Agency Information Processing Techniques Office (DARPA IPTO), Tech. Rep*, vol. 15, 2008.

- 11 Moody, A. *et al.*, "Design, modeling, and evaluation of a scalable multi-level checkpointing system," in *SC'10: Proceedings of the 2010 ACM/IEEE International Conference for High Performance Computing, Networking, Storage and Analysis*. IEEE, 2010, pp. 1–11.
- 12 Wang, C. *et al.*, "Hybrid checkpointing for mpi jobs in hpc environments," in *2010 IEEE 16th International Conference on Parallel and Distributed Systems*. IEEE, 2010, pp. 524–533.
- 13 Weiland, M. *et al.*, "An early evaluation of intel's optane dc persistent memory module and its impact on high-performance scientific applications," in *Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*, 2019, pp. 1– 19.
- 14 Wu, Y. *et al.*, "Lessons learned from the early performance evaluation of intel optane dc persistent memory in dbms," in *Proceedings of the 16th International Workshop on Data Management on New Hardware*, 2020, pp. 1–3.
- 15 Weiland, M. *et al.*, "Usage scenarios for byte-addressable persistent memory inhigh-performance and data intensive computing," *arXiv preprint arXiv:2012.06473*, 2020.
- 16 Peng, I. *et al.*, "Demystifying the performance of hpc scientific applications on nvm-based memory systems," in *2020 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*. IEEE, 2020, pp. 916–925.
- 17 Wu, K., "Runtime data management on non-volatile memory-based high performance systems," Ph.D. dissertation, University of California, Merced, 2021.
- 18 Christgau, S. *et al.*, "Leveraging a heterogeneous memory system for a legacy fortran code: The interplay of storage class memory, dram and os," in *2020 IEEE/ACM Workshop on Memory Centric High Performance Computing (MCHPC)*. IEEE, 2020, pp. 17–24.
- 19 Ren, J. *et al.*, "Optimizing large-scale plasma simulations on persistent memory-based heterogeneous memory with effective data placement across memory hierarchy," in *Proceedings of the ACM International Conference on Supercomputing*, 2021, pp. 203–214.
- 20 Malinowski, A. *et al.*, "Multi-agent large-scale parallel crowd simulation with nvram-based distributed cache," *Journal of Computational Science*, vol. 33, pp. 83–94, 2019.
- 21 Garg, S. *et al.*, "The need for precise and efficient memory capacity budgeting," in *The International Symposium on Memory Systems*, 2020, pp. 169–177.
- 22 Zhu, G. *et al.*, "An empirical evaluation of nvm-aware file systems on intel optane dc persistent memory modules," in *2021 International Conference on Information Networking (ICOIN)*. IEEE, 2021, pp. 559–564.
- 23 Bother, M. ¨ *et al.*, "Drop it in like it's hot: An analysis of persistent memory as a drop-in replacement for nvme ssds," in *Proceedings of the 17th International Workshop on Data Management on New Hardware (DaMoN 2021)*, 2021, pp. 1–8.
- 24 Soumagne, J. *et al.*, "Accelerating hdf5 i/o for exascale using daos," *IEEE Transactions on Parallel and Distributed Systems*, 2021.
- 25 Lopez-G ´ omez, J. ´ *et al.*, "Exploring object stores for high-energy physics data storage," *arXiv preprint arXiv:2107.07304*, 2021.
- 26 Wong, P. *et al.*, "Nas parallel benchmarks i/o version 2.4," *NASA Ames Research Center, Moffet Field, CA, Tech. Rep. NAS-03-002*, 2003.
- 27 Ren, J. *et al.*, "Easycrash: Exploring non-volatility of non-volatile memory for high performance computing under failures," *arXiv preprint arXiv:1906.10081*, 2019.
- 28 Zvi, K. *et al.*, "Optimized memoryless fair-share hpc resources scheduling using transparent checkpoint-restart preemption," *arXiv preprint arXiv:2102.12953*, 2021.
- 29 Ren, J. *et al.*, "Exploring non-volatility of non-volatile memory for high performance computing under failures," in *2020 IEEE International Conference on Cluster Computing (CLUSTER)*. IEEE, 2020, pp. 237– 247.
- 30 McAnlis, J. C. *et al.*, "Data processor system including data-save controller for protection against loss of volatile memory information during power failure," Jul. 3 1984, uS Patent 4,458,307.
- 31 Peng, I. B. *et al.*, "System evaluation of the intel optane byte-addressable nvm," in *Proceedings of the International Symposium on Memory Systems*, 2019, pp. 304–315.
- 32 Scargall, S., *Introducing the Persistent Memory Development Kit*. Berkeley, CA: Apress, 2020, pp. 63–72. [Online]. Available: https: //doi.org/10.1007/978-1-4842-4932-1 5
- 33 Axboe, J., "Fio-flexible io tester," http://freshmeat.sourceforge.net/ projects/fio, 2014.

- 34 Izraelevitz, J. *et al.*, "Basic performance measurements of the intel optane dc persistent memory module," *arXiv preprint arXiv:1903.05714*, 2019.
- 35 Xu, J. *et al.*, "NOVA: A log-structured file system for hybrid volatile/non-volatile main memories," in *14th USENIX Conference on File and Storage Technologies (FAST 16)*. Santa Clara, CA: USENIX Association, Feb. 2016, pp. 323–338. [Online]. Available: https: //www.usenix.org/conference/fast16/technical-sessions/presentation/xu
- 36 Bailey, D. H. *et al.*, "The nas parallel benchmarks," *The International Journal of Supercomputing Applications*, vol. 5, no. 3, pp. 63–73, 1991.
- 37 Pouchet, L.-N. *et al.*, "PolyBench Benchmarks," https://web.cse. ohio-state.edu/∼pouchet.2/software/polybench/, [Online].
- 38 Bailey, D. H., "Nas parallel benchmarks," in *Encyclopedia of Parallel Computing*. Springer, 2011, pp. 1254–1259.
- 39 Yuki, T., "Understanding polybench/c 3.2 kernels," in *International workshop on Polyhedral Compilation Techniques (IMPACT)*, 2014, pp. 1–5.
- 40 Gabriel, E. *et al.*, "Open mpi: Goals, concept, and design of a next generation mpi implementation," in *European Parallel Virtual Machine/Message Passing Interface Users' Group Meeting*. Springer, 2004, pp. 97–104.
- 41 Tristian, T. *et al.*, "Analyzing the performance of intel optane dc persistent memory in app direct mode in lenovo thinksystem servers," 2019.
- 42 "Quick Start Guide Part 1: Persistent Memory Provisioning Introduction," https://software.intel.com/content/www/us/en/develop/ articles/qsg-intro-to-provisioning-pmem.html, [Online].
- 43 Kadekodi, R. *et al.*, "SplitFS: Reducing Software Overhead in File Systems for Persistent Memory," in *Proceedings of the 27th ACM Symposium on Operating Systems Principles (SOSP '19)*, Ontario, Canada, October 2019.
- 44 Lu, Y. *et al.*, "Octopus: an rdma-enabled distributed persistent memory file system," in *2017 USENIX Annual Technical Conference (USENIX ATC 17)*. Santa Clara, CA: USENIX Association, Jul. 2017, pp. 773–785. [Online]. Available: https://www.usenix.org/conference/atc17/ technical-sessions/presentation/lu
- 45 Anderson, T. E. *et al.*, "Assise: Performance and availability via client-local NVM in a distributed file system," in *14th USENIX Symposium on Operating Systems Design and Implementation (OSDI 20)*. USENIX Association, Nov. 2020, pp. 1011–1027. [Online]. Available: https://www.usenix.org/conference/osdi20/presentation/anderson
- 46 Liang, Z. *et al.*, "Daos: A scale-out high performance storage stack for storage class memory," in *Supercomputing Frontiers*, Panda, D. K., Ed. Cham: Springer International Publishing, 2020, pp. 40–54.
- 47 "DAOS official documentation website," https://daos-stack.github.io/, [Online].
- 48 Kwon, Y. *et al.*, "Strata: A cross media file system," ser. SOSP '17. New York, NY, USA: Association for Computing Machinery, 2017, p. 460–477. [Online]. Available: https://doi.org/10.1145/3132747.3132770
- 49 "Assise's Github issue #7," https://github.com/ut-osa/assise/issues/7, [Online].
- 50 "Assise's Github issue #3," https://github.com/ut-osa/assise/issues/3# issuecomment-838785034, [Online].
- 51 "POSIX Namespace DAOS v1.2," https://daos-stack.github.io/user/ posix/, [Online].
- 52 "Scalable Checkpoint / Restart (SCR) Library github page." https://github. com/LLNL/scr, [Online].
- 53 "Scalable Checkpoint / Restart (SCR) Library documentation page." https: //scr.readthedocs.io/en/latest/, [Online].
- 54 Ansel, J. *et al.*, "DMTCP: Transparent checkpointing for cluster computations and the desktop," in *2009 IEEE International Symposium on Parallel & Distributed Processing (IPDPS'09)*. Rome, Italy: IEEE, 2009, pp. 1– 12.
- 55 Rodr´ıguez-Pascual, M. *et al.*, "Job migration in hpc clusters by means of checkpoint/restart," *The Journal of Supercomputing*, vol. 75, no. 10, pp. 6517–6541, 2019.
- 56 Cao, J. *et al.*, "Transparent Checkpoint-Restart over InfiniBand," *HPDC 2014 - Proceedings of the 23rd International Symposium on High-Performance Parallel and Distributed Computing*, Dec. 2013.
- 57 Maronas, M. ˜ *et al.*, "Extending the openchk model with advanced checkpoint features," *Future Generation Computer Systems*, vol. 112, pp. 738– 750, 2020.
- 58 "Aurora Argonne Leadership Computing Facility," https://alcf.anl.gov/ aurora, 2021, [Online].
- 59 "Intel® Optane™ persistent memory (PMem)," https://www. intel.com/content/www/us/en/products/details/memory-storage/ optane-dc-persistent-memory.html, [Online].
- 60 "NegevHPC Project," https://www.negevhpc.com, [Online].

