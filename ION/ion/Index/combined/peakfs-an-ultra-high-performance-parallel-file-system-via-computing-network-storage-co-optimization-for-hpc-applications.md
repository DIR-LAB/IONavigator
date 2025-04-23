# PeakFS: An Ultra-High Performance Parallel File System via Computing-Network-Storage Co-Optimization for HPC Applications

Yixiao Chen , Haomai Yang, Kai Lu , Wenlve Huang , Jibin Wang, Jiguang Wan , Jian Zhou , Fei Wu *, Member, IEEE*, and Changsheng Xie *, Member, IEEE*

*Abstract***—Emerging high-performance computing (HPC) applications with diverse workload characteristics impose greater demands on parallel file systems (PFSs). PFSs also require more efficient software designs to fully utilize the performance of modern hardware, such as multi-core CPUs, Remote DirectMemory Access (RDMA), and NVMe SSDs. However, existing PFSs expose great limitations under these requirements due to limited multi-core scalability, unaware of HPC workloads, and disjointed networkstorage optimizations. In this article, we present PeakFS, an ultrahigh performance parallel file system via computing-networkstorage co-optimization for HPC applications. PeakFS designs a shared-nothing scheduling system based on link-reduced task dispatching with lock-free queues to reduce concurrency overhead. Besides, PeakFS improves I/O performance with flexible distribution strategies, memory-efficient indexing, and metadata caching according to HPC I/O characteristics. Finally, PeakFS shortens the critical path of request processing through network-storage co-optimizations. Experimental results show that the metadata and data performance of PeakFS reaches more than 90% of the hardware limits. For metadata throughput, PeakFS achieves a 3.5–19**× **improvement over GekkoFS and outperforms BeeGFS by three orders of magnitude.**

#### *Index Terms***—Parallel file system, high-performance computing, remote direct memory access, performance optimization.**

Received 3 July 2024; revised 24 September 2024; accepted 15 October 2024. Date of publication 24 October 2024; date of current version 8 November 2024. This work was supported in part by the National Key Research and Development Program of China under Grant 2023YFB4502701, in part by the National Natural Science Foundation of China under Grant 62072196, in part by the Key Research and Development Program of Guangdong Province under Grant 2021B0101400003, and in part by the Creative Research Group Project of NSFC under Grant 61821003. Recommended for acceptance by D. Tiwari. *(Yixiao Chen and Haomai Yang are co-first authors.) (Corresponding author: Kai Lu.)*

Yixiao Chen, Haomai Yang, Kai Lu, Wenlve Huang, Jiguang Wan, Jian Zhou, Fei Wu, and Changsheng Xie are with the Wuhan National Laboratory for Optoelectronics, Huazhong University of Science and Technology, Wuhan 430074, China (e-mail: chenyixiao@hust.edu.cn; m202173462@hust.edu.cn; kailu@hust.edu.cn; huangwenlve@hust.edu.cn; jgwan@hust.edu.cn; jianzhou @hust.edu.cn; wufei@hust.edu.cn; cs_xie@hust.edu.cn).

Jibin Wang is with the Key Laboratory of Computing Power Network and Information Security, Ministry of Education, Shandong Computer Science Center (National Supercomputer Center in Jinan), Qilu University of Technology (Shandong Academy of Sciences), Jinan 250353, China, and also with the Shandong Provincial Key Laboratory of Computing Power Internet and Service Computing, Shandong Fundamental Research Center for Computer Science, Jinan 250000, China (e-mail: wangjb@sdas.org).

Digital Object Identifier 10.1109/TPDS.2024.3485754

#### I. INTRODUCTION

T HE rapid advancements in high-performance computing (HPC) have revolutionized scientific research [1], [2], engineering simulations [3], [4], and data-intensive applications, such as Big Data analytics [5], [6] and AI training [7], [8]. These emerging HPC systems and applications pose higher challenges for storage systems. First, *more new types of I/O workloads emerged*, such as intensive access to small files and data sharing patterns [9], [10], [11], which are challenging for storage systems. Second, *hardware device upgrades*. For example, modern supercomputers are equipped with multi-core processors, high-speed networks (e.g., Remote Direct Memory Access, RDMA), and fast, large-capacity storage devices (e.g., NVMe SSDs). The performance bottleneck has shifted from the hardware to the software side. However, traditional parallel file systems (PFSs) often used in HPC systems (e.g., Lustre [12], BeeGFS [13], GPFS [14]) have struggled to meet the demanding requirements of emerging HPC applications due to limitations in performance and scalability [15], [16], [17].

Recently, researchers in both industry and academia have proposed novel file systems to overcome I/O performance bottlenecks, including HPC-oriented solutions (e.g., GekkoFS [15], HadaFS [17]), metadata-oriented solutions (e.g., InfiniFS [18], SingularFS [19]), and hardware-oriented optimization (e.g., PolarFS [20], DAOs [21]). We re-examine the designs of many new PFSs in this paper. Our main observation is that existing PFSs have substantial potential for improvement to better support emerging HPC applications and modern hardware, due to the limitations in computing, network, and storage. The three challenges are summarized as follows:

- 1) *Limited multi-core scalability:* In order to utilize the capabilities of multi-core CPUs, PFSs need to schedule multiple threads well to reduce resource contention between threads and achieve high concurrency. A major challenge of traditional architectures is that lock contention overhead scales rapidly with the number of tasks and CPU cores [20], [22]. Especially for ultra-high performance PFSs, each lock can be a performance bottleneck. A promising lock-free way is to shard separate resources for different threads [20]. However, in large-scale HPC systems with numerous nodes, the task dispatching between
1045-9219 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

nodes and scheduling between threads become extremely challenging.

- 2) *Unaware of HPC workloads:* The storage backends of most PFSs do not consider HPC I/O characteristics adequately, resulting in suboptimal I/O performance. From a distributed perspective, current metadata and data distribution strategies mainly make trade-offs between load balancing and locality. These fixed and inflexible strategies lead to data over-skewing or over-dispersion under diverse HPC workloads. Moreover, from a single-node perspective, the general-purpose key-value stores (e.g., RocksDB [23]) or databases are often used as metadata engines [15], [16], and the underlying file systems (e.g., EXT4) are as data engines [13], [24]. However, they are not designed for HPC file system and lack optimization of indexing and caching strategies based on HPC workloads, which limits the performance of PFSs.
- 3) *Disjointed network-storage optimizations:* Modern network and storage optimization techniques, such as RDMA [25] and asynchronous I/O APIs [26], [27], are widely used in HPC PFSs, improving the efficiency of network transfers and access to NVMe SSDs. However, simply using these techniques in different components (e.g., network, storage) does not reduce some critical path latency of request processing, such as network pipeline blocking under consecutive write requests (common HPC workloads, Section II-A) and SSD I/Os for read requests. In addition, most PFSs tend to focus on performance scaling within a single network/storage module, while neglecting co-optimization with other modules, causing extra overhead (e.g., memory copies) or even sacrificing some performance [24].

In this paper, we propose an ultra-high performance parallel file system for HPC applications, called *PeakFS*. The significant feature of PeakFS is to achieve computing-network-storage cooptimization based on HPC I/O characteristics and modern hardware features. Specifically, PeakFS advocates three optimized designs to address the aforementioned challenges: 1) PeakFS proposes a high-concurrency, lock-free scheduling system to improve the efficiency of multi-thread processing based on a shared-nothing architecture and link-reduced task dispatching with lock-free queues. 2) PeakFS designs an HPC-oriented storage backend with flexible metadata/data distribution, efficient in-memory indexes, and metadata caches to deliver high performance for both metadata and data. 3) PeakFS employs networkstorage co-optimizations with non-blocking write pipeline and end-to-end zero-copy, to reduce latency of write/read requests. We implement and evaluate PeakFS using metadata and data benchmarks. The evaluation results demonstrate the ultra-high metadata and data performance of PeakFS, which reaches more than 90% of the hardware limits. For typical metadata operations such as small file create and stat, PeakFS achieves up to 19× and 3.5× higher performance compared to the state-ofthe-art HPC file system (GekkoFS), and surpasses traditional parallel file system (BeeGFS) by three orders of magnitude.

In summary, we have the following contributions:

- We summarize the I/O behavior characteristics of emerging HPC applications and modern hardware features, and analyze the performance limitations of current PFSs in their computing, network, and storage designs (Section II).
- We design and implement PeakFS (Section III), an ultrahigh performance PFS for HPC applications, featured with shared-nothing concurrent scheduling (Section III-B), HPC workload-aware storage backend (Section III-C), and network-storage co-optimizations (Section III-D).
- We conduct a comprehensive evaluation of PeakFS's performance and compare it with state-of-the-art PFSs (Section IV). The results demonstrate that PeakFS significantly outperforms these systems in terms of performance, scalability, and utilization of hardware capabilities.

#### II. BACKGROUND AND MOTIVATION

## *A. HPC Applications I/O Behavior Analysis*

The ever-increasing I/O demands of HPC applications pose challenge to PFSs. An in-depth understanding of the HPC application I/O behavior can provide guidance for file system design and optimization. From the studies including Cori supercomputer [10], [11], Lawrence Livermore National Laboratory [28], [29], Nurion supercomputer [30], and representative HPC benchmarks [9], [31], we summarize that modern HPC applications have the following I/O characteristics:

- C1 *Continuous access of the same I/O type:* Modern HPC applications largely tend to perform only-one-type I/O (write or read) in a single run and HPC files experience a few consecutive write/read requests over a period of time [10], [11], [28].
- C2 *Shared I/O pattern and intensive access to small files:* Files are often shared by multiple applications, and Tirthak Patel et al. [10] found that over 67% of files are accessed by at least 2 applications. Compared to fileper-process (called N-N) I/O pattern, shared file (called N-1) I/O pattern is the difficulty for PFSs [15], [16], [17]. Additionally, some studies indicate that most files of many HPC applications are small files [32], [33], which is challenging for PFSs [9].
- C3 *Heavy metadata operations and unbalanced metadata loads:* Modern HPC applications include large numbers of metadata operations [15], [33]. For example, Arnab K. Paul et al. [28] found that there is a positive correlation between metadata operations and writes. Metadata access easily becomes a system performance bottleneck [18], [34],[35]. In addition, the study [28] also found that metadata distributed across metadata servers is unbalanced, which can adversely impact the I/O performance.
- C4 *Lots of memory remains unused for I/O operations:*Arnab K. Paul et al. [28] found that more than 95% of applications write in bursts occupying less than 5% of memory. Therefore, we can ideally use more memory portions in an HPC storage system to improve the overall I/O performance.

- C5 *Weaker semantics requirements:* Many studies suggest that most HPC applications have relaxed semantic requirements, including 1) POSIX I/O interfaces. Some studies [15], [31] show that lots of HPC applications uses only a small set of metadata operations, and many operations (e.g., chown, utime) are not used. 2) Consistency semantics. Wang et al. [31] categorizes the consistency semantic guarantees and finds that 17 typical HPC applications surveyed do not require strict consistency requirements; they only need *commit consistency* semantics or more relaxed semantics.
#### *B. Modern Hardware Technologies*

The emergence of new hardware technologies, such as multicore CPUs, RDMA networks, and NVMe SSDs, offers the opportunity to develop higher performance PFSs.

*Multi-core CPUs* have become the norm in HPC systems driven by the need to increase computing power and efficiency [36]. Additionally, multi-core CPUs are more powerefficient than single-core CPUs, as they can distribute workloads across multiple cores, reducing the overall power consumption. For instance, Intel Xeon Gold 6433N @3.6 GHz processor released in 2023 has 32 cores. Kunpeng 920 processor@2.6 GHz can support up to 64 cores. However, multi-core CPUs place higher demands on software design, and the ability of multi-core CPUs to increase application performance depends on the use of multiple threads within applications [37]. On the other hand, ARM-based processor architectures are becoming common and popular in HPC systems due to power-efficient, low cost, and scalability [38].

*RDMA* is a series of protocols that enable direct data access from one machine to remote ones over the network. RDMA protocols are typically solidified directly on RDMA NICs (RNICs), offering high bandwidth (≥ 100 Gbps) and low latency at the microsecond level (∼ 2 µs). These protocols are widely supported by InfiniBand, RoCE, OmniPath, etc.[39]. RDMA provides data transfer services based on two types of operational primitives: *one-sided verbs* including RDMA READ, WRITE, ATOMIC (e.g., FAA, CAS) and *two-sided verbs* including RDMA SEND, RECV. RDMA communication is implemented through a message queue model called the Queue Pair (QP) and the Completion Queue (CQ). CQ is associated with the specified QP. Once the sender's request completes, the RNIC writes the completion entry to CQ, so that the sender can know it by polling CQ.

*NVMe SSDs* provide faster data transfer and lower latency over PCIe compared to legacy protocols like SAS, SATA. For example, Samsung's PM9A3 SSD can deliver up to 850 K IOPS (random read) and 6800 MB/s (sequential read) [40]. However, the legacy kernel I/O stack becomes the bottleneck as SSDs are getting faster [20]. Therefore, more storage stacks are proposed and become popular [27], including libaio, io_uring, Storage Performance Development Kit (SPDK), etc. The first two are commonly used asynchronous I/O APIs in Linux storage stacks. SPDK [26] is a user-space I/O libraries that completely bypasses the kernel, which can deliver up to 10 million IOPS using a single CPU core.

![](_page_2_Figure_8.png)

Fig. 1. Latency test of GekkoFS.

#### *C. Limitations of Existing PFSs*

We find that modern PFSs don't support emerging HPC workloads well and don't fully utilize the hardware performance, which is the main motivation of this paper. We revisit PFSs released in recent years and summarize three distinct performance limitations:

## Limitation 1. *Thread scheduling suffers from multi-core CPU scalability issues due to lock overheads.*

Efficient thread scheduling is critical to leverage the performance of multi-core CPUs. The multi-thread scheduling strategies in existing PFSs have two distinct features: 1) *Pipeline* mode. Each I/O request is divided into several phases, and the processing of each phase corresponds to a thread pool [35], [41]. 2) *Shared-everything* or *shared-disk* mode. All threads share resources, and explicit or implicit locks are required to support concurrent access [15]. These architectures suffer from significant multi-core scalability issues, with overhead from: 1) *context-switches for thread switching*; 2) *locks for synchronization and mutual exclusion between multiple threads* [20], [22].

For example, GekkoFS [15] and UnifyFS [24] use lightweight thread pools [42] on the server side. They rely on the concurrency capability of the backend storage. Taking GekkoFS as an example, all threads share a common RocksDB [23] instance for metadata access and a common underlying file system (e.g., EXT4) for reading and writing data. As shown in Fig. 1(a), we use GekkoFS's scheduling strategy to allow several threads to access a shared hashtable [43] (see Section IV-F for more details). The results indicate that more than 90% of the latency overhead is due to locking.

Recently, many PFSs [20], [22] also attempt to use *sharednothing* thread model [44] on the server side to achieve lock-free scheduling. For example, in PolarFS [20], each I/O thread (on a dedicated core) handles all phases of an I/O request, using separate RDMA and NVMe queue pairs. To achieve a shared-nothing architecture on the server side, a naive approach is to establish connections between all client processes and all I/O threads, known as *full-mesh mode*. This mode consumes a large amount of RNIC resources and increases latency, which is especially pronounced in larger-scale HPC systems [25]. Techniques such as *Hugepages* and *QP-sharing* [45] can alleviate this problem, but there are issues such as the lock contention of shared QPs

![](_page_3_Figure_1.png)

Fig. 2. Metadata Create throughput of BeeGFS and GekkoFS under different workloads.

between threads[25], [46]. Therefore, it is challenging to design shared-nothing scheduling architectures for HPC file systems.

- Limitation 2. *Inflexible metadata distributions and inefficient indexes fail to deliver optimal performance due to lack of awareness of HPC workloads.*
To improve I/O performance, many file systems propose efficient distribution strategies and storage engines. However, they do not pay deep attention to HPC workload characteristics and have many limitations in HPC scenarios.

First, current metadata/data distribution strategies make tradeoffs between balance and locality. For example, many PFSs (e.g., GekkoFS, HadaFS [17]) adopt a full-pathname indexing approach (distributed via hashing), achieving excellent load balancing and good scalability. The example of GekkoFS is shown in Fig. 2. However, they sacrifice locality and make the hierarchy semantic (e.g., rename) difficult to implement. In addition, many file systems (e.g., HopsFS [47], BeeGFS [13], InfiniFS [18]) adopt fine-grained partitioning and group related metadata while sharding for good load balancing and high metadata locality. These fixed distribution methods have advantages in some scenarios, but are not always optimal in HPC applications with diverse workloads. For example, for a big shared directory with lots of small files (C2 in Section II-A, common HPC workloads), these approaches can lead to a large amount of data skewed in a single metadata shard, resulting in long-tail latency. Fig. 2 shows that BeeGFS has good scalability under multiple directories, but suffers from scalability issues under shared-directory workloads.

Second, out-of-the-box storage engines fail to fully utilize memory resources. Many PFSs abandon the underlying file system (e.g., EXT4) and choose key-value stores (e.g., MD-HIM [16], [48], RocksDB [23]) or databases (e.g., NDB [47], [49], TafDB [34]) as metadata engines. However, these generalpurpose metadata engines are not designed for PFS workloads and still fall short in performance due to reliability and functionality requirements. For example, RocksDB, a popular LSMbased key-value storage, has great write performance but sacrifices read performance [50], which can not meet the fast querying requirements of PFS multi-layer path resolution. Furthermore, their memory indexes and caches are not designed for PFSs, which are inefficient in HPC scenarios and do not fully utilize the limited memory resources.

## Limitation 3. *Optimizing network and storage respectively via RDMA and asynchronous I/O do not reduce some critical path latency of request processing.*

RDMA network and asynchronous I/O interfaces (e.g., SPDK, libaio) are widely used in modern PFSs to improve request processing efficiency. However, we find that there are still many high latency operations (problems/bottlenecks) along the critical path of request processing that these techniques fail to address. In addition, some unnecessary overhead are caused due to disjointed network-storage optimizations. We take GekkoFS as an example. GekkoFS uses the existing scheduling framework Argobots[42] to achieve asynchronous I/O, the RDMA network framework Mercury [51], and adopts Margo [52] to bind them together. As shown in Fig. 1(b), we measure the latency of GekkoFS under metadata create operations and data read operations (see Section IV-D for more details). We observe that GekkoFS has long-latency processing paths due to the following issues:

- 1) *RPC request blocking:* GekkoFS adopts asynchronous blocking RDMA to handle write requests, i.e., the client sends the write request to the server via RDMA SEND, then the server persists the data and sends the response back. A write request is completed only when the client receives a response (RECV), and the next write request starts. When faced with continuous write requests (HPC workload characteristic C1), GekkoFS suffers from request blocking, resulting in long latency network paths.
- 2) *SSD I/Os:* The data path is dominated by the access to SSDs, which cannot be reduced by asynchronous I/O. According to HPC I/O characteristic (C4), designing efficient caching policies is a promising measure to reduce SSD I/Os.
- 3) *Extra memory-copy operations:* Since GekkoFS directly uses the existing network framework and underlying file system, some implicit memory copies may be caused between user buffer, network buffer, and I/O buffer [53]. These unnecessary memory-copy operations increase processing latency.

Even worse, some PFSs optimize a module but sacrifice the performance of another module. For example, UnifyFS broadcasts some detailed metadata to all servers, which improves file read/write bandwidth while significantly disrupting metadata performance.

#### III. PEAKFS DESIGN

#### *A. PeakFS Overview*

To address the above challenges, we propose *PeakFS*, an ultrahigh performance parallel file system for HPC applications. Based on the I/O characteristics of HPC applications and new hardware features, PeakFS adopts computing-network-storage co-optimization technologies to achieve near-optimal performance. PeakFS has three key design ideas as below:

- *Shared-nothing task scheduling with lock-free exchange queues (Section III-B):* PeakFS proposes a shared-nothing
Fig. 3. PeakFS overview.

thread architecture, allowing each thread to hold independent resource slices without locking overhead. PeakFS designs a link-reduced task dispatching method with lockfree queues to reduce the number of network connections and increase the efficiency of request processing.

- *HPC workload-aware distribution and memory-efficient metadata indexing (Section III-C):* PeakFS provides multiple flexible metadata/data distribution strategies to meet diverse HPC workloads. Additionally, PeakFS proposes a path-aware, compact in-memory index structure tailored to PFS to accelerate metadata indexing. PeakFS also designs client- and server-side metadata caches to minimize SSD access and enhance metadata performance.
- *Shortening the critical path through network-storage cooptimizations (Section III-D):* In addition to adopting RDMA and SPDK, PeakFS further reduces latency of write/read requests through non-blocking write pipeline and read cache with read-ahead mechanism based on HPC I/O characteristics. Moreover, PeakFS achieves full-path zero-copy through network-storage co-optimizations.

The overall architecture of PeakFS is shown in Fig. 3. PeakFS consists of a master, many clients and servers. The master node is used for information exchange, resource monitoring, etc. The servers register the addresses for RDMA link establishment with the master via TCP at startup and periodically report the storage usage. HPC applications preload the client interception library (*Client Lib*) at startup, then connect to servers. The client lib intercepts file system operations (*Syscall Hook*) and forwards them to servers via a RPC framework (pRPC). The client maintains the mapping of file descriptors of open files and directories (*File Map*). A PeakFS server consists of a scheduling system (*RingSched*), a pRPC server and a storage backend (*PStore*). The server receives forwarded RPC requests from clients, processes them using RingSched and PStore, and sends responses when finished. PeakFS supports most POSIX file system APIs, including file reading and writing, directory scanning, etc., but does not support hard links or directory permission operations. In addition, PeakFS provides less strict consistency semantics[31], i.e., *commit consistency semantics*, which is sufficient for most HPC applications (C5) [15], [17], [24].

### *B. Shared-Nothing Concurrent Scheduling*

In order to fully utilize the performance of modern multi-core CPUs and improve the efficiency of multi-thread processing,

![](_page_4_Figure_9.png)

Fig. 4. Shared-nothing scheduling architecture (in a server).

![](_page_4_Figure_11.png)

Fig. 5. Network links and task dispatching.

PeakFS proposes a high concurrency, lock-free, and fully asynchronized scheduling system, called *RingSched*. As shown in Fig. 4, RingSched per server mainly consists of a *worker thread* pool, a stateless *memcpy thread* pool, and lock-free queues for exchanging requests between threads.

*Shared-nothing thread architecture:* To solve the Limitation 1, RingSched enables lock-free access to resources through the shared-nothing thread architecture. Each worker thread's PStore slice holds a non-shared, private physical space on the SSD (called a *Zone*) for storing metadata and data. A worker thread has both communication and processing functions. Therefore, when handling client requests, the request is first sent to a server based on PeakFS's resource distribution strategy (Section III-C1), then received by the corresponding communicating thread based on link-reduced task dispatching method (described later), and finally forwarded to the correct processing thread (Section III-C1) via lock-free queues. The entire processing of a request is done by its processing thread to avoid thread switching (i.e., run-to-completion, RTC model).

*Link-reduced task dispatching:* To solve full-mesh problems in Limitation 1, PeakFS adopts a shared link method to connect clients and servers. As shown in Fig. 5, PeakFS establishes fixed network connections between clients, server-side RNICs, and worker threads (WTs) in a round-robin way. For client i connecting to a server, the corresponding server RNIC is (i mod *RNIC*_num), and the corresponding communicating thread is (i mod *thread*_num). All requests from client i to the server are first aggregated at the communicating thread and then forwarded to their processing threads. This means that only one RDMA link is set up on the server for client i and the client's RDMA QP is only allowed to be processed by the communicating thread, avoiding performance degradation due to the lock contention of QPs between threads [25], [46]. Take an example in Fig. 5, client 0 is connected to RNIC 0 and WT0, and it sends a request for the storage slice held by WT2. WT0 at server side receives the RPC request from RNIC 0 and forwards the request to WT2 by the lock-free queues. With this method, PeakFS can reduce the number of network connections and balance multi-RNIC resources.

*Fully asynchronous processing:* RingSched needs to handle both fast RPC requests (e.g., create, stat) and timeconsuming RPC requests (e.g., write, read). To avoid worker threads being blocked by network transfers and SSD I/Os, PeakFS supports asynchronous transfer and I/O with RDMA and SPDK asynchronous programming. In addition, we still find that some memory copy (memcpy) operations are timeconsuming (Section III-D). The memcpy operations can be accelerated using the Intel I/OAT DMA engine [54], but there is no such engine in the Arm environment. Thus, RingSched sets up a dedicated memcpy thread pool to asynchronize memcpy operations. Denoting the total network bandwidth as nb and the memory copy speed of a single memcpy thread as mb, the memcpy thread pool size can be estimated by *nb/mb*. When the data size to be copied is greater than a threshold (e.g., 4 KiB), the worker thread sends the request through a lock-free queue to a stateless memcpy thread. It is then sent back to the original thread after the memcpy operation has been processed. RingSched reduces long-tail latency and avoids being blocked by any time-consuming operations by processing requests fully asynchronously.

*Lock-free task exchange queue:* We achieve exchange queues based on DPDK rte_ring [55], which provides singleproducer (SP) or multi-producer (MP), single-consumer (SC) or multi-consumer (MC) modes. As shown in Fig. 4, to improve the utilization and performance of lock-free queues, we carefully chose the producer and consumer modes: a multiple SPSC queues for exchanging tasks between worker threads;b a single MPMC queue for worker threads to send requests to memcpy threads; c multiple MPSC queues for memcpy threads to send back responses to the worker threads. This design is based on the following reasons: 1) For the producer setting, since a occurs in almost every request, the multiple SP queues are used to improve performance [56] and achieve better fairness. b /c only occurs when a request hits the read cache (Section III-D) and happens less frequently, so the use of MP queues increases the effective number of queue outs and prevents queue idling. 2) For the consumer setting, the destination of b can be any memcpy thread, so a single MC queue is used for random thread assignment. The destination of a /c is a deterministic worker thread. Therefore, a /c uses multiple SC queues for sending to a fixed destination.

As shown in the example in Fig. 4, RingSched processes I/O requests as follows:1 The worker thread 0 gets the RPC request from the network; 2 Thread 0 sends I/O requests through the SPSC queue to the worker thread 1 that owns the resource slice; 3 If a memcpy operation is required, it is sent to the memcpy thread via the MPMC queue. Otherwise, the worker thread submits an asynchronous SPDK operation in a zone; 4 The memcpy or data read/write operations complete; 5 The worker thread 1 sends back the response to thread 0. Then, 6 thread 0 sends the RPC response back to the client. Considering that the communicating thread and the processing thread are usually not the same thread (Section III-C1), the typical forward count for an I/O request is 2 (without memcpy thread) or 4 (with memcpy thread). Nonetheless, a lock-free queue typically takes only a few tens of nanoseconds for a single operation, so RingSched's task forwarding strategy still delivers higher performance (Section IV-F).

#### *C. HPC-Oriented Storage Backend*

To improve I/O performance and fully utilize fast NVMe SSDs based on HPC workload characteristics, we design a novel HPC-oriented storage backend,*PStore*, which includes metadata engine (PMeta) and data engine (PData).

- *PMeta* supports directory trees and there are two kinds of metadata in PMeta: directory entry (*dentry* for short) and *inode*. A single dentry keeps a name component of a file path and has a reference to an inode. A collection of dentries are organized into a directory tree. An inode describes the attribute of either a regular file or a directory. For dentry, PMeta designs a novel radix tree-like index structure to store and index dentry. For inode, PMeta uses a bitmap for assigning the inode to a certain location in the metadata zone, and adopts a hashtable for maintaining the mapping of inode number (ino) to the inode's SSD offset (*inode offset* for short).
- *PData:* In PData, each worker thread holds a data zone on the SSD, which is divided into a number of equal-sized pages (called *data pages*). PData divides files into multiple file blocks and uses a bitmap to assign several consecutive data pages for a file block in the data zone. PData also adopts a hashtable to maintain the mapping of file blocks to data pages. All hashtables use write-ahead logs (WALs) to ensure recovery.

The core optimizations of PStore are load distribution (distributed view) and metadata access (single-node view), to improve load balancing and performance.

*1) Flexible Metadata and Data Distribution:* According to characteristic C2 (i.e., shared pattern and small file features), PeakFS provides multiple distribution strategies based on different directory sizes and different data sharing modes, which can be specified by directory or file attributes, environment variables, configurations, and other hints.

*Metadata distribution based on directory sizes:* PMeta adopts different metadata distribution strategies for the regular directory (dir for short) and big directory (*bigdir* for short, which has many sub-files). a For a regular dir, the inodes of its sub-dirs are sharded to different servers via hashing. PMeta places other related metadata of its sub-dirs (including dentry) or sub-files (including dentry and inode) on the server with its inode, as shown in Fig. 6(a). Such a design sacrifices limited balancing to improve the locality, and reduces one round-trip time (RTT) for obtaining inode. b For a bigdir, the metadata of its sub-dirs or sub-files is sharded to different servers as shown in Fig. 6(b). The access to sub-dentry/sub-inode can be distributed to different servers to improve processing efficiency and avoid the data skew issues. Users can select an appropriate metadata distribution

![](_page_6_Figure_1.png)

Fig. 6. Metadata distribution strategies.

strategy based on a prior knowledge, or default to the bigdir strategy so that the metadata is always distributed in a balanced manner.

*Data distribution based on sharing modes:* PData provides three data distribution strategies: a *Block-based:* By default, PData distributes file blocks to servers according to the hash value of ino and block number. For small files, PData assigns the first file block to the server that holds the inode of the file, and directly saves the mapping of the first file block to the data pages in the inode. After the client obtains the inode, it can directly access the first file block, reducing one RTT. b *Filebased:* For N-N I/O patterns, PData hashes files to servers at the granularity of the entire file rather than the file block. This is because N-N files are often read continuously [16], and this distribution can better leverage spatial locality. c *I/O-based:* For equal-size and non-overlapping I/O patterns, the consecutive data pages corresponding to an I/O are exclusive to only the I/O and the invalid part is filled with blanks. When the write request size is not a multiple of the SPDK sector size, an extra read I/O for aligning the I/O buffer to the SPDK sector size can be avoided by I/O-based distribution.

The route of a request through RingSched is determined by a characteristic value λ, which is calculated from the request information and the distribution strategy. For example, the λ of a create request in a bigdir is *hash*(*parent*_*ino, f ilename*), while the λ of a block-based write request is *hash*(*ino, block*_id). Client i's request is sent to server λ mod *server*_num, received by communicating thread i mod *thread*_num, and handled by processing thread λ*/server*_num mod *thread*_num. Therefore, choosing distribution strategies flexibly can better distribute requests to servers and worker threads. This approach avoids the trade-offs between scalability and locality that result from using a single distribution strategy. As a result, it meets the demands for balance and locality across various workloads.

*2) PFS-Specific Metadata Index Structure:* To solve Limitation 2 (i.e., limitations of generic metadata engines), PMeta proposes a PFS-specific index structure and designs different caching strategies for different metadata, to make full use of memory resources and enhance metadata performance.

*Path-aware compact dentry indexing:* Before accessing the file's inode, PFS often needs to resolve the path by querying several layers of dentries in the directory tree based on filename and other information. Storing dentries in server's memory can speed up querying, but it takes up a lot of memory. Therefore, PMeta proposes a *fast, compact* index structure based on the adaptive radix tree (ART,[57]), called *cART*, to accelerate dentry indexing. A cART example of a worker thread is shown in Fig. 7(a), where the bigdir's two sub-files happen to be sliced into this thread. The dentry key is *(pino, fname)*, where *pino* is the ino of the parent directory and *fname* is the filename of the sub-directory or sub-file. For the regular dir metadata distribution strategy, the dentry value is the ino for sub-directories or the inode offset for sub-files. For the bigdir metadata distribution strategy, the dentry value is the inode offset for both sub-directories and sub-files. cART adopts multiple ARTs to index the dentry values, and adopts a hashtable for maintaining the mapping of pino to the root node of an ART. When accessing a dentry, the ART root is first queried in the hashtable via pino, and the dentry value is obtained by querying the corresponding ART based on fname.

Considering that filenames in the same directory may have the same prefixes or suffixes and often contain highly structured information (dates, serial numbers, etc.) [58], cART adopts the following strategies based on the filename characteristics of HPC PFSs to improve ART's performance and save more memory space:

a *Multiple-sized nodes:* Since filenames in PFS usually consist of just uppercase and lowercase letters, Arabic numerals, and a few symbols, letting every cART node have a fixed number of child nodes to accommodate all possible characters would lead to wasted space. Thus, cART provides several different numbers of child nodes, allowing a node to dynamically scale up and down. As shown in Fig. 7(b), cART has three child node size options: *Node256*, *Node64* and *Node16*. The largest node is Node256, meaning that the node can have 256 child nodes, which is the maximum value of a byte. Node64 can hold structured filenames, e.g., uppercase and lowercase letters, Arabic numerals, and two extra spaces. Node16 can hold number information, e.g., Arabic numerals and six additional spaces. The node size can be selected based on the number of existing child nodes and can be converted. Different from ART, the key array size in a cART node is always equal to the node size, so the process of finding a child node according to the key in Node16 or Node64 can also be optimized with SIMD instructions [57] such as SSE or AVX512.

b *Prefix compression:* Due to the fact that filenames in the same directory may have the same prefixes, cART can compress the common key prefix of multiple dentries to save space. As shown in Fig. 7(c), there are existing dentries with fname "data1", "data2". Their common prefixes ("data") can be compressed, retaining only the two distinct letters. When

![](_page_7_Figure_1.png)

![](_page_7_Figure_2.png)

another dentry with fname "dxyz" is inserted, the common prefix is extracted from the existing node, retaining the distinct parts.

c *Node consolidation:* As shown in Fig. 7(d), cART further reduces space by consolidating nodes. In cART, the node's key array and val array store the characters and values of each child node, respectively. The node also stores the common prefix at the end of the val array, so its key array stores the first distinct character after the common prefix (e.g., "1", "2"). In this way, logically distinct nodes are merged into a single node in the actual data structure. Splitting and merging of nodes are also triggered when prefixes change due to adding or deleting a dentry. When a node splits and wants to modify its prefix, the original node (e.g., old in Fig. 7(d)) only needs to adjust the prefix length, rather than reallocating a piece of memory to hold the new prefix. This avoids the memory allocate/free overhead and memory fragmentation associated with storing prefixes separately.

d *Leaf-node compression:* Since the dentry value (ino or inode offset) is a 64-bit integer with the same number of bits as a pointer, cART also proposes a leaf node compression scheme, as shown in Fig. 7(d). cART stores the values of the leaf nodes (e.g., ino) in the val array of the parent node (e.g., *new2*), thereby saving space and reducing node accesses.

*Client dentry cache:* The depth of the directory tree in PFSs can reach 10 layers or more [18]. Therefore, an inode operation requires 10 or more RPCs to access dentries, which can severely degrade performance. PMeta designs a dentry cache on the client side to reduce the number of remote RPCs. To ensure performance, PMeta uses lightweight distributed *tokens* to maintain consistency of the dentry cache. At any given time, a directory may grant multiple read tokens (*shared*) or only one write token (*exclusive*), and the clients that acquire these tokens are also recorded. When accessing a dentry, the dentry can be cached in client after obtaining a read token from the dentry's parent directory. When modifying/deleting this dentry, the client needs to broadcast to all clients that have obtained the read tokens to invalidate them, and obtains the write token of the parent directory. To reduce broadcasting, each token is set with an expiration time on both the client and server sides, and only a small amount of infrequently changing dentries are cached. This means that since deleting and moving directories account

for only 0.2% of operations under most workloads [18], [34], the client only caches dentries whose child nodes are directories. The client neither caches dentries whose child nodes are files nor acquires tokens for them, to avoid frequent dentry cache invalidation.

*Local inode cache:* To accelerate inode access, PMeta sets a fixed number of inode cache blocks (called *Icache*) in each server's memory and uses a hashtable to index Icaches. It is worth noting that the inode cache is not maintained on clients because inodes are updated frequently, and caching them on clients would result in significant consistency maintenance overhead. As shown in Fig. 8(a), each Icache caches a fixed number of inodes (e.g., K). According to the dentry value, inode can be accessed through ino or SSD offset.When using ino to read/write a inode (e.g., ino = 123), the corresponding SSD offset (e.g., 17) of the ino is first get from the inode hashtable. The cache array is used to query whether there is a corresponding Icache with the index number *offset/K* (e.g., 17/K). If there is an Icache, access the in-memory Icache to fetch the inode; if not, trigger an Icache update.

PMeta manages Icaches via a state machine to achieve a high cache hit rate, as shown in Fig. 8(b). PeakFS server allocates a number of Icaches with initial state (free) at startup. When an Icache misses, it enters the *read* state to read inodes from the SSD to fill it, and enters the *ready* state once the read is finished. When there is no free Icache, an Icache in the ready state is converted to free state according to the least-recently-used (LRU) rule. When modifing an inode in an Icache, the Icache enters the *dirty* state. The server limits the maximum ratio of dirty Icaches in the total Icaches (e.g., 5%). Once the maximum dirty ratio is exceeded, a dirty Icache is selected based on the LRU rule to enter the *write* state, writes the inodes to the SSD, and then returns to the *ready* state once completed. Due to the dirty ratio limit and the flexible metadata distribution strategies, it is easy for PMeta to implement inode cache prefetching, which allows the inode cache to reach a hit rate of 99%.

#### *D. Network-Storage Co-Optimizations*

To solve Limitation 3, PeakFS proposes non-blocking pipeline for write RPCs on the client side and uses read cache

Fig. 8. Inode layout and cache.

Fig. 9. Write request pipeline.

on the server side to reduce latency of write/read requests. Furthermore, PeakFS eliminates most memory copies on the endto-end path through network-storage co-optimizations, while asynchronously handling necessary memcpy copies.

*Non-blocking pipeline for consecutive writes:* PeakFS supports commit consistency semantics (meets C5 in Section II-A), which guarantee that data written by write will be readable after fsync or close. This is enough for most HPC applications to run correctly [17], [31]. Based on characteristic C1, pRPC improves write performance by pipelining consecutive write requests to return earlier after these requests are successfully sent out, as shown in Fig. 9(b). The traditional write process (Fig. 9(a)) has to block the client and wait for the previous write request to complete before starting the next one. In contrast, PeakFS significantly speeds up write request processing. To guarantee commit consistency, pRPC sets up a count variable *unf inished*_cnt, which means the number of write requests that are submitted but did not complete the data persistence. The send operation of a write request is completed when the SEND success (i.e., the RDMA CQ generates a work completion of SEND). PeakFS adds 1 to the *unf inished*_cnt of the file being written and the client can send the next write request. When the server completes data persistence and sends the response back, *unf inished*_cnt of the file is reduced by 1. When the client needs to make sure the data is persisted, it will call fsync or close and wait for *unf inished*_cnt to be zeroed before returning. The *unf inished*_cnt has an upper limit to control the number of unpersistent write requests.

![](_page_8_Figure_6.png)

*End-to-end zero-copy: no silver bullet:* PeakFS integrates network and storage to achieve end-to-end zero-copy when the read cache is not involved. Since PeakFS provides a memory allocator for applications to transparently allocate user buffer in the RDMA memory region (MR), the user buffer on the client side can be used as a network buffer without copy. Therefore, 1) When the client sends a write request, it uses an RDMA scatter/gather list to concatenate the data in the user buffer with the RPC header and adds padding, then sends it via RDMA SEND. Since the server's network buffer is also registered as DMA buffer, it can be used as an I/O buffer to write data to the SSD, avoiding an extra memory copy from the network buffer to the I/O buffer on the server side. 2) When the client sends a read request, it uses RDMA SEND to send the address of the client's user buffer and other information to the server. The server reads the data and writes it directly to the client's user buffer via RDMA WRITE, avoiding an extra memory copy from the network buffer to the user buffer on the client side. However, the read cache is not registered as MR, so the data will be asynchronously copied to a network buffer by the memcpy thread pool (Section III-B) before WRITE. This is because registering the space-consuming read cache as MR may cause a larger number of cache misses in the RNIC's memory translation table [59],[60], leading to even worse performance than memory copying. Another reason is that registering the read cache as MR for zero-copy RDMA WRITE will occupy the read cache longer than copy and WRITE, hindering read cache reuse.

#### IV. EVALUATION

#### *A. Experiment Setup*

*Environment:* All experiments are conducted on a 13-node heterogeneous cluster including a master node, 6 client nodes and 6 server nodes. Each node is equipped with two 100 Gbps Mellanox ConnectX-6 MT4123 InfiniBand RNICs. Each client

![](_page_8_Figure_12.png)

![](_page_8_Figure_13.png)

node is equipped with two Intel Xeon Gold 5318Y CPUs @2.6 GHz (each 24 cores and 48 threads), 512 GB DRAM, and no SSDs. Each master/server node is equipped with an ARM-based 64-core Kunpeng 920 CPU @2.6 GHz, 256 GB DRAM, and ten 1.5TB NVMe SSDs. The operating system is Red Hat Enterprise Linux (RHEL) 8 with the kernel version 4.18.0. Each SSD has a maximum 2100 MiB/s write bandwidth and 3300 MiB/s read bandwidth. We can roughly estimate the SSD write bandwidth to be 10 × 6 × 2100 MiB/s = 123 GiB/s, SSD read bandwidth to be 10 × 6 × 3300 MiB/s = 193 GiB/s, and the RDMA network bandwidth to be 6 × 200 Gb/s = 139 GiB/s in the entire experimental cluster. So, the cluster is I/O-bound during writes and network-bound during reads.

*Comparisons:* PeakFS is compared with two other opensource PFSs: 1) *BeeGFS* [13], a parallel cluster file system designed for HPC, and 2) *GekkoFS* [15], a temporary file system for HPC applications. We execute BeeGFS with version v7.4.0, and GekkoFS with version v0.9.1. However, the original GekkoFS can not run properly due to the poor compatibility between Mercury (GekkoFS's communication framework) and our ARM-based test environment. Therefore, we modify the GekkoFS source code to add the ability to use multiple SSDs and RNICs, and replace the I/O engine with libaio. Our tests have shown that the performance is even better than its original version [15]. To ensure a fair comparison, these PFSs disable features such as replication, availability, and other features that are not relevant to performance optimization.

*Deployment:* GekkoFS and PeakFS mount the PFS client by specifying the syscall interceptor library on the client node. Each server node deploys a server process that manages 10 SSDs to store metadata and data. The file block size is 64 KiB. Each PFS server runs 60 worker threads, and PeakFS also runs 4 memcpy threads. Each worker thread is assigned to a dedicated core and runs in polling mode. BeeGFS mounts the PFS client by compiling and inserting the kernel module. On the server nodes, BeeGFS deploys the metadata service using 1 SSD and the data service using 9 SSDs, as a metadata service supports only one target. We tuned BeeGFS with the parameters recommended in the official documentation [61]. Before each round of experiments, we restart the PFS and clear the SSDs as well as the memory cache.

*Workloads:* 1) We use the *mdtest* [62] and IOR [63] benchmarks in the experimental cluster to test the metadata and data performance of these PFSs, and whether PeakFS can fully leverage computing and network performance. The workloads generated in this experiment are similar to the IO500 benchmark [9]. First, we fix the number of processes per node to 48 and vary the number of client and server nodes, comparing the performance and scalability of these PFSs (Sections IV-B and IV-C). Next, we fix the number of client and server nodes to 6, and vary the number of processes per node to provide a more in-depth analysis of PeakFS's performance under different client pressures (Section IV-D). 2) We use three more realistic HPC benchmarking tools (*md-workbench* [64], *HACC-IO* [65], and *MADbench2* [66]) in another small-scale I/O-bound test environment to test the comprehensive performance of these PFSs, and evaluate whether PeakFS can fully leverage storage performance (Section IV-E). 3) We test several of PeakFS's key techniques separately to understand their impact on performance and memory efficiency (Section IV-F).

#### *B. Metadata Performance Results*

To demonstrate the metadata performance and scalability of these PFSs, we had mdtest perform create, stat, and remove operations on *empty* and *small* files in this test. Each client process's empty files are stored in a separate directory, while small files (3901 bytes) from all processes are stored in a shared directory. PeakFS uses the regular metadata distribution strategy for empty files and the bigdir metadata distribution strategy for small files (Section III-C1). A file is not accessed for stat, or delete operations by its creating process to disturb the page cache. All PFSs need to run the create operation for at least 50 seconds to create enough files for testing.

Figs. 10 and 11 show metadata throughputs (KIOPS) of different operations on empty and small files. It can be seen that compared to BeeGFS and GekkoFS, PeakFS exhibits an overwhelming performance advantage. Specifically, based on the results, the following conclusions can be drawn:

- 1) PeakFS and GekkoFS exhibit good scalability on all workloads, with performance growing essentially linearly as the number of nodes increases. With no centralized nodes, the ability to resolve near-root hotspot through client dentry cache, and flexible metadata distribution strategies, we believe PeakFS will also exhibit good scalability in larger systems. However, BeeGFS scales poorly on a shared directory with many small files.
- 2) PeakFS outperforms GekkoFS and BeeGFS by a large margin on all metadata operations. As shown in Fig. 10, PeakFS's metadata throughput is two orders of magnitude higher than BeeGFS, and several times higher than GekkoFS. PeakFS has up to 400× and 7.0× higher create throughput than BeeGFS and GekkoFS. Also, PeakFS has 137× and 8.4× higher throughput on stat operation, and 608× and 3.4× on delete operation. The ultra-high metadata performance of PeakFS is due to the computing-network-storage co-optimization. RingSched framework makes PeakFS linearly scaling performance. In addition, compared to GekkoFS's metadata storage (RocksDB) and BeeGFS's metadata storage (EXT4), PMeta's fast indexing and caching strategies allow PeakFS to access metadata with near-memory performance.
- 3) PeakFS's metadata performance improvement is more pronounced under small-file workloads, which achieves up to 2560×/19× higher throughput than BeeGFS/GekkoFS for create, and 672×/3.5× for stat, as shown in Fig. 11. In addition to the high-performance metadata engine, PeakFS employs other optimizations for small files. Due to lots of small files in the shared directory, PeakFS uses the bigdir metadata distribution strategy (Section III-C1), improving processing efficiency. In addition, PeakFS adopts many optimizations for reading and writing small files, such as storing the first block map in the inode (Section III-C1).

![](_page_10_Figure_2.png)

Fig. 10. Metadata performance on *empty files*.

![](_page_10_Figure_3.png)

Fig. 11. Metadata performance on *small files*.

GekkoFS also has good scalability due to full-pathname hash distribution. However, BeeGFS has limited metadata performance due to the large number of small files being processed on a single metadata server.

#### *C. Data Performance Results*

To demonstrate the data performance and scalability of these PFSs, we had IOR perform write and read operations on files with N-N and N-1 I/O patterns in this test. For N-N (fileper-process) pattern, each process accesses its own file, and the transfer size for each I/O is 256 KiB. For N-1 (shared file) pattern, all processes access the same shared file, and the transfer size for each I/O is 47008 bytes. The amount of read-ahead data per client is configured to 10 times transfer size by default. PeakFS uses the file-based data distribution strategy for the N-N I/O pattern and the I/O-based data distribution strategy for the N-1 I/O pattern (Section III-C1). The I/Os do not overlap and each client process only reads data written by other processes to disturb the page cache. All PFSs need to run the write operation for at least 40 seconds to write enough data for testing.

Figs. 12 and 13 show data bandwidth (GiB/s) comparison of different operations with N-N and N-1 I/O patterns. Based on the results, the following conclusions can be drawn:

(1) PeakFS and GekkoFS exhibit excellent scalability under all workloads, and the scalability of PeakFS is slightly better than that of GekkoFS. Take Fig. 12(b) as an example, the scalability ratio (*bandwidth*6 *nodes*/(*bandwidth*1 *node* × 6) ) of PeakFS is 98.3%, higher than GekkoFS's 92.7%. We also believe that the flexible data distribution strategies can help PeakFS exhibit

![](_page_10_Figure_10.png)

![](_page_10_Figure_11.png)

![](_page_10_Figure_12.png)

![](_page_10_Figure_13.png)

![](_page_10_Figure_14.png)

![](_page_10_Figure_15.png)

![](_page_10_Figure_16.png)

![](_page_10_Figure_17.png)

Fig. 12. Data performance under N-N I/O pattern.

![](_page_10_Figure_19.png)

Fig. 13. Data performance under N-1 I/O pattern.

excellent scalability in larger systems. However, BeeGFS scales poorly under N-1 read workload.

(2) PeakFS can significantly improve data access performance, with read/write bandwidth reaching or approaching hardware limits. As shown in Fig. 12, PeakFS has 4.2× and 1.7× higher write bandwidth, and 4.0× and 2.3× higher read bandwidth compared to BeeGFS and GekkoFS, respectively.

![](_page_11_Figure_1.png)

Fig. 14. Metadata performance of *empty files* under different processes.

Compared to BeeGFS, which directly uses EXT4 file system to store data, the modified GekkoFS improves read/write concurrency with the asynchronous I/O interface libaio. PeakFS uses the user-level SPDK to further reduce kernel overhead. In addition, PeakFS uses pipelined writes, read caching, and zero-copy strategies (Section III-D) to improve read and write performance.

(3) PeakFS has no performance degradation in more stringent shared I/O patterns. As shown in Fig. 13, both BeeGFS and GekkoFS show performance degradation under N-1 I/O mode compared to N-N I/O mode. In comparison, PeakFS maintains high performance under N-1 I/O mode due to the I/O-based data distribution strategy (Section III-C1), which avoids the overhead incurred by aligning the SPDK sector size. As a result, under N-1 workloads, PeakFS has 48× and 4.6× higher write bandwidth than BeeGFS and GekkoFS, and improves read bandwidth by 17× and 3.4×, respectively.

#### *D. In-Depth Analysis*

*Different Processes:* To test the performance of different PFSs under different client pressures, we keep the number of client/server nodes at 6, set the number of processes per client node from 6 to 48, and rerun the experiments in Sections IV-B and IV-C. 1) Metadata results. Fig. 14 shows the metadata create and stat performance on empty files. It is evident that BeeGFS reaches the peak performance with 6–12 client processes per node, while GekkoFS peaks at 24 client processes per node. In contrast, PeakFS demonstrates a consistent performance increase as the number of client processes rises, reaching a plateau only when the client process count matches the upper limit of 48 (CPU core limit). This suggests that PeakFS offers higher concurrency compared to GekkoFS and BeeGFS. 2) Data results. Fig. 15 shows the data performance with N-N I/O pattern. The results still show PeakFS's advantages in concurrency and leveraging multi-core CPUs. It is worth noting that PeakFS exhibits a bandwidth fluctuation on write operations. Since the file-based distribution is adopted for N-N pattern, each worker thread faces varying request pressure when the number of processes is not an integer multiple of the number of SSDs, leading to long-tail latency. However, due to high processing efficiency, the overall performance of PeakFS improves as the pressure increases and PeakFS rapidly reaches the hardware bandwidth limit. Furthermore, the read bandwidth of PeakFS does not exhibit any fluctuations. This is because when the

![](_page_11_Figure_7.png)

Fig. 15. Data performance of N-N I/O pattern under different processes.

![](_page_11_Figure_9.png)

Fig. 16. Latency decomposition.

workload pressure is low, the SSD read bandwidth is not fully utilized, and PeakFS's read bandwidth is limited by the network hardware bandwidth under high pressure.

*Latency Decomposition:* To analyze the performance improvement of PeakFS in detail, we measured the latency for the computing, network, and storage parts of PeakFS and GekkoFS when processing metadata and data requests. We calculate network latency by subtracting the latencies of other parts from the total latency, so the network latency includes both network transmission time and waiting-for-processing time. For metadata create operation, Fig. 16(a) shows that PeakFS has negligible storage and computing latency (around 0.5 µs) compared to GekkoFS, due to the more efficient metadata indexing and caching of PeakFS (Section III-C2) compared to RocksDB used by GekkoFS. PeakFS's efficient metadata processing and shared-nothing concurrent scheduling (Section III-B) also reduce waiting-for-processing time, resulting in lower network latency (around 7 µs) compared to GekkoFS. For data read operation, Fig. 16(b) shows that PeakFS's I/O latency (largest part) is half that of GekkoFS. PeakFS improves read performance by replacing SSD I/O with memcpy through read cache and read-ahead mechanisms, and by implementing zero-copy on the client side (Section III-D).

*Reaching Hardware Limits:* For metadata stat operation, we estimate the performance ceiling of the experimental cluster based on network speed. The full-duplex rate for sending and receiving metadata requests on each RNIC is 9.5 MIOPS. Each server node has two RNICs and 60 worker threads, so the latency for a worker thread to send or receive a packet is 1 9.5×2/60 = 3.16 µs. Fig. 16(a) shows that the non-network latency for PeakFS to process a metadata request is only 1 µs, which is difficult to reduce further and can be considered a lower bound. Therefore, a metadata request requires a minimum

![](_page_12_Figure_1.png)

processing time of 3.16 + 1 + 3.16 = 7.32 µs, and the throughput ceiling for metadata operations in the experimental cluster is 6 × 60/7.32 = 49.18 MIOPS. Due to limited CPU cores, each client node runs 48 processes, fewer than the 60 worker threads on each server node. With the metadata distribution strategy for a regular dir and link-reduced task dispatching, only 48/60 = 80% worker threads are fully utilized when running the test in Fig. 10(b). As a result, the maximum metadata stat throughput that PeakFS can deliver in the experimental cluster is 35758.92/(80% × 1000) = 44.7 MIOPS, reaching 90.9% of the hardware limit. For data read operation, PeakFS can reach 129.61/139 = 93.2% of the hardware limit, as shown in Fig. 12(b).

#### *E. Comprehensive Experiments in an I/O-Bound Environment*

To understand the storage performance capabilities of these PFSs, we tested their comprehensive performance in another I/O-bound small-scale test cluster, handling workloads closer to HPC applications. This cluster has 1 server node and 1 client node. Each node is equipped with two Intel Xeon Gold 5218R CPU @2.1 GHz (each 20 cores and 40 threads), 128 GB DRAM, two Samsung 990 PRO SSDs and one 100 Gbps Mellanox ConnectX-5 MT4119 RNIC. Since the SSD write bandwidth of 6040 MiB/s and read bandwidth of 6250 MiB/s for the server node are less than the network bandwidth, the cluster is I/O-bound. Each PeakFS or GekkoFS server runs 12 worker threads, and PeakFS also runs 2memcpythreads. The client runs 36 client processes. Through these tests, we will demonstrate that PeakFS can efficiently handle diverse HPC workloads and fully leverages storage performance.

*Mixed Metadata-Intensive Workloads: md-workbench* [64] is a benchmark to measure metadata and data performance of small files by simulating parallel compilation on PFS. The workload generated by md-workbench is similar to the small file workload in Section IV-B, but the metadata and data operations are mixed, making it more difficult to be optimized with caching compared to staged I/O. Fig. 17 shows the mixed throughput (KIOPS) of different metadata and data operations on small files after running md-workbench for at least 30 seconds. The mixed throughput of PeakFS is 5.5× higher than GekkoFS and 23× higher than BeeGFS. Despite md-workbench limiting the read cache of PeakFS, PeakFS still delivers higher performance with its efficient shared-nothing scheduling (Section III-B) and PFS-specific metadata indexing (Section III-C2).

*Checkpoint/Restart Workloads: HACC-IO* [65] is the I/O kernel of a cosmology N-body simulation application HACC. It

![](_page_12_Figure_7.png)

![](_page_12_Figure_8.png)

Fig. 19. Performance of the I/O kernel for matrix saving and loading.

simulates the process of saving and loading particle information between HACC's computing stages, i.e., checkpoint/restart workloads. In this test, each process handles 32 million particles and uses the N-N I/O pattern. Fig. 18 shows the bandwidth of the PFSs on checkpoint/restart workloads. PeakFS outperforms GekkoFS by only 6% and BeeGFS by 8%, as the workloads are simple and all PFSs approach the storage performance limit.

*Matrix Saving/Loading Workloads. MADbench2* [66] is an I/O kernel derived from a cosmic microwave background data analysis application. It simulates the process of exchanging data between processes through matrix saving/loading and uses busywork instead of real computations, focusing on HPC application I/O behavior while maintaining application complexity. In this test, 16 matrices of size 24 576 × 24 576 are processed for each PFS. All data is written to a shared file using the N-1 I/O mode, and we made a few code modifications to ensure the commit consistency semantics is enough for MADbench2.1 Fig. 19 shows the bandwidth of the PFSs on matrix saving/loading workloads. Considering that the transfer size is a multiple of the libaio block size, GekkoFS shows improved relative bandwidth compared to Fig. 13, reducing the advantages of PeakFS's I/O-based distribution strategy. Nevertheless, PeakFS continues to achieve 15× and 1.2× higher write bandwidth, and 3.2× and 1.6× higher read bandwidth compared to BeeGFS and GekkoFS, respectively. PeakFS also reaches the storage performance limit. MADbench2 simulates the full process of application computation and I/O with lower I/O frequency. Therefore, PeakFS's network-storage co-optimizations (Section III-D) can bring storage performance improvements in this scenario.

<sup>1</sup>The modified code, along with the detailed parameters and running scripts for the other tests in Sections IV-B, IV-C, IV-D, and IV-E, can be found at https://github.com/poorpool/peakfs-experiments.

![](_page_13_Figure_1.png)

Fig. 20. Indexing performance with different scheduling.

![](_page_13_Figure_3.png)

Fig. 21. Performance comparison and memory usage of different indexes.

#### *F. Impact of Key Technologies*

*RingSched Test:* To evaluate the advantages of RingSched, we implement RingSched (shared-nothing, SN for short) and GekkoFS's scheduling strategies (shared-everything, SE for short) on different index structures (Hashtable [43] and RocksDB [23]), and test the throughput of put, get, and delete operations using 20 threads (each thread run 25 million operations). We create 20 hashtables in memory, and 20 RocksDB on 10 SSDs first. For SN, each thread holds a hashtable/RocksDB. The target thread is calculated based on the hash value of the key and the request is forwarded to the thread for processing through a lock-free queue. For SE, each request selects the hashtable/RocksDB by key hashing. Concurrent control is guaranteed by locking for hashtable and guaranteed by RocksDB itself. As shown in Fig. 20, regardless of hashtable or RocksDB, RingSched can improve performance by 2–6× compared to shared-everything architecture on all operations. RingSched avoids lock overhead and has significant performance advantages. In addition, we compared the efficiency of exchanging requests using 20 × 20 SPSC lock-free queues and 20 MPSC lock-free queues. The former achieved 1.05–1.3× higher performance than the latter.

*cART Test:* We test the performance of cART with two hash indexes (unordered_map and unordered_dense [43]), traditional ART [67], and Masstree [68]. We use 20 threads to constantly put, get and delete key-value pairs. Each thread uses a private index structure to handle 25 million key-value pairs. To simulate consecutive files, the key consists of a fixed prefix of 12 bytes and two sequentially growing numeric serial numbers, with the three parts separated by a dot. The values are 32-bit integers. Fig. 21(a) shows that cART delivers better performance than other index structures for all the three operations, and Fig. 21(b)

![](_page_13_Figure_8.png)

Fig. 22. Impact of PeakFS's strategies on performance.

demonstrates that the memory usage of cART is only 1/5 of other index structures. The reasons include: 1) cART is optimized for PFS workloads; 2) cART is more compact through prefix compression and leaf-node compression; 3) cART stores prefixes in its node's val array, avoiding the overhead of numerous small memory allocate/free operations (Section III-C2).

*Write Pipeline and Read Cache:* Fig. 22 shows the impact of PeakFS's write pipeline (WP) and read cache (RC) strategies on write and read performance (using IOR with N-1 workloads in Section IV-C). It can be found that these strategies significantly improve write performance and read performance. However, the optimization of write pipeline is not obvious when the number of processes is 48. This is because when the workload pressure is high, server-side storage backend can not process writes in time, blocking write requests. Therefore, this feature has no significant improvement under higher pressures.

#### V. RELATED WORK

*PFSs for HPC Applications:* Many HPC systems introduce SSDs to form burst buffers as an I/O acceleration layer [69]. Some PFSs are proposed to fully utilize burst buffers and reduce I/O time for HPC applications.

BurstFS [16] aggregates small read requests for multidimensional variables on the server side to improve read performance. However, BurstFS only supports local writes and uses a distributed key-value store to maintain the mapping of file offset ranges to server IDs (also known as data location information). This can lead to unbalanced data distribution and requires querying multiple key-value servers to retrieve the data location information before reads, which increases read latency, especially for small files. PeakFS uses flexible data distribution strategies to balance file data and reduce read latency for small files.

UnifyFS [24] also requires clients to write data locally. UnifyFS stores all data location information of a file on a node using a red-black tree and caches this information on other nodes, improving the efficiency of querying this information compared to BurstFS. On the other hand, UnifyFS broadcasts the data location information to all servers, regardless of whether it is needed, causing excessive network communication. PeakFS writes data to remote servers and does not need to maintain data location information. PeakFS only stores the dentries of sub-directories on the client side to accelerate path resolution, thus avoiding excessive cache maintenance requests caused by frequent file operations.

GekkoFS [15] divides file data into equal-sized blocks and distributes both file metadata and blocks across servers using full-pathname hashing, providing excellent scalability and balanced load distribution. GekkoFS uses RocksDB to store metadata and the underlying file system (e.g., EXT4) to store data with strong consistency semantics. GekkoFS's thread pool relies on the concurrency control capabilities of these out-ofthe-box storage engines. However, these storage engines are not designed for HPC workloads, leaving room for performance improvement (Section II-C). PeakFS designs an HPC-oriented storage backend to fully leverage performance. It includes a PFS-specific metadata index structure and various caches to improve metadata and data read performance. Additionally, PeakFS uses a lock-free shared-nothing thread architecture to improve concurrency.

HadaFS [17] deploys burst buffers on I/O forwarding nodes. Each client process selects an I/O forwarding node and always writes file data to that node. Thus, HadaFS essentially performs "local" writes, similar to BurstFS and UnifyFS, providing good write performance while still requiring the maintenance of data location information. PeakFS can achieve similar benefits under N-N workloads by using the file-based data distribution strategy, without maintaining data location information. HadaFS maintains a local metadata database and a shard of the global metadata database on each I/O forwarding node. By configuring the synchronization strategy between the two metadata databases, HadaFS offers three consistency semantics and performance levels, providing richer options compared to PeakFS. However, since HadaFS uses the same storage engines as GekkoFS, it similarly has potential for performance optimization.

*Efficient Large-Scale Metadata Service:* InfiniFS [18] decouples directory metadata into content parts (e.g., sub-dentries) and access parts (e.g., permissions). InfiniFS distributes the content part by hashing the directory ID and stores the sub-directory's access part together with the parent directory's content part, achieving both high metadata locality and effective load balancing. However, InfiniFS's partitioning strategy places the metadata of all sub-files in a directory on the same node, making it difficult to distribute the metadata load of big directories. PeakFS designs different metadata distribution strategies for regular directories and big directories, thus achieving similar optimizations to InfiniFS for regular directories and distributing the metadata load evenly for big directories. SingularFS [19] explores partitioning strategies similar to InfiniFS and concurrency control in timestamp updates, but only uses a single metadata server.

HopsFS [47] and CFS [34] use distributed databases to store and distribute metadata, aiming to provide rich and even POSIXcompliant metadata semantics. HopsFS transforms file system metadata into the Entity-Relationship model for storage and uses complex distributed locks to maintain file system consistency. CFS adopts a partitioning strategy similar to InfiniFS to store metadata in a distributed key-value database. CFS further distributes file attributes by hashing file IDs to achieve load balance even under the big directory cases. Additionally, CFS introduces new database primitives based on metadata semantics and prunes critical sections to improve database performance. However, these designs are not tailored for HPC scenarios and are too heavy for high-performance PFSs that only use a subset of metadata operations.

*Other High-Performance File Systems:* Many distributed file systems aim for higher performance by leveraging new hardware or adapting to different scenarios. For instance, DAOS [21] explores methods for using persistent memory in user space to store metadata, thereby constructing a scale-out file system. PolarFS [20] is a low-latency, high-availability distributed file system designed for cloud database services. PolarFS uses a shared-nothing architecture, RDMA, and SPDK, and is therefore possibly the most relevant work to PeakFS in terms of technical choices. Nonetheless, PolarFS is designed for storing large database chunks, focusing on improvements to consistency protocols rather than workload distribution or storage engine performance optimization, making it less suitable for HPC scenarios. PeakFS, in contrast, focuses on exploring how to fully utilize hardware performance through computing-network-storage co-optimization to meet the I/O demands of HPC applications.

#### VI. DISCUSSION

PeakFS analyzes the typical HPC I/O characteristics and optimizes performance for the primary use cases, but it may not be perfect for all scenarios. First, PeakFS supports commit consistency semantics and employs techniques like write pipeline to enhance performance. Therefore, user must ensure that the corresponding data has been flushed using fsync or close before initiating a read operation; otherwise, undefined data may be read. Second, PeakFS uses link-reduced task dispatching to reduce the number of RDMA links between client processes and worker threads. However, it is challenging to fully utilize the server's storage capability when the client scale is smaller than the server's. Third, PeakFS has diverse but static distribution strategies for metadata and data. Currently, PeakFS cannot migrate loads when the load distribution changes dynamically.

Moving forward, we plan to make PeakFS applicable to a wider range of scenarios, with the same good performance using less a priori knowledge. In the future, we plan to offer users a configurable option to disable the write pipeline feature, supporting strong consistency semantics and meeting the I/O requirements of more HPC applications. Additionally, we plan to make task dispatching more flexible and implement migratable load distribution strategies, allowing PeakFS to utilize server resources more effectively and evenly in hybrid scenarios. We also look forward to expanding PeakFS beyond the HPC domain, leveraging its outstanding performance to accelerate upper-layer applications, such as large language model inference, high frequency trading, and Big Data analysis.

#### VII. CONCLUSION

This paper presents PeakFS, an ultra-high performance file system for modern HPC applications. PeakFS reduces thread scheduling overhead by shared-nothing and full-asynchronous processing; then improves I/O performance by designing flexible distribution strategies and memory-efficient indexing/caching techniques; and finally, improves request processing efficiency by network-storage co-designs, including write pipeline and end-to-end zero-copy. Evaluation shows that PeakFS significantly outperforms other HPC file systems.

#### REFERENCES

- [1] K. M. Tolle, D. S. W. Tansley, and A. J. Hey, "The fourth paradigm: Data-intensive scientific discovery [point of view]," *Proc. IEEE*, vol. 99, no. 8, pp. 1334–1337, Aug. 2011.
- [2] Z. Liu et al., "SunwayLB: Enabling extreme-scale lattice Boltzmann method based computing fluid dynamics simulations on sunway taihulight," in *Proc. 2019 IEEE Int. Parallel Distrib. Process. Symp.*, 2019, pp. 557–566.
- [3] Y. Ye et al., "swNEMO_v4.0: An ocean model based on NEMO4 for the new-generation sunway supercomputer," *Geoscientific Model Develop.*, vol. 15, no. 14, pp. 5739–5756, 2022.
- [4] J. Xiao et al., "Symplectic structure-preserving particle-in-cell wholevolume simulation of tokamak plasmas to 111.3 trillion particles and 25.7 billion grids," in *Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal.*, 2021, pp. 1–13.
- [5] H. M. Makrani, S. Rafatirad, A. Houmansadr, and H. Homayoun, "Mainmemory requirements of big data applications on commodity server platform," in *Proc. 18th IEEE/ACM Int. Symp. Cluster Cloud Grid Comput.*, 2018, pp. 653–660.
- [6] B. Schmidt and A. Hildebrandt, "Next-generation sequencing: Big data meets high performance computing," *Drug Discov. Today*, vol. 22, no. 4, pp. 712–717, 2017.
- [7] A. Coates, B. Huval, T. Wang, D. Wu, B. Catanzaro, and N. Andrew, "Deep learning with COTS HPC systems," in *Proc. Int. Conf. Mach. Learn.*, 2013, pp. 1337–1345.
- [8] L. Floridi and M. Chiriatti, "GPT-3: Its nature, scope, limits, and consequences," *Minds Mach.*, vol. 30, pp. 681–694, 2020.
- [9] J. Kunkel, J. Bent, J. Lofstead, and G. S. Markomanolis, "Establishing the IO-500 benchmark," *White Paper*, 2016.
- [10] T. Patel et al., "Uncovering access, reuse, and sharing characteristics of I/O-intensive files on large-scale production HPC systems," in *Proc. 18th USENIX Conf. File Storage Technol.*, 2020, pp. 91–101.
- [11] J. Bang et al., "HPC workload characterization using feature selection and clustering," in *Proc. 3rd Int. Workshop Syst. Netw. Telemetry Analytics*, 2020, pp. 33–40.
- [12] P. Braam, "The lustre storage architecture," 2019, *arXiv: 1903.01955*.
- [13] Beegfs, the leading parallel file system, 2023. [Online]. Available: https: //www.beegfs.io/c/
- [14] F. Schmuck and R. Haskin, "GPFS: A shared-disk file system for large computing clusters," in *Proc. Conf. File Storage Technol.*, 2002, pp. 19–es.
- [15] M.-A. Vef et al., "GekkoFS-A temporary distributed file system for HPC applications," in *Proc. 2018 IEEE Int. Conf. Cluster Comput.*, 2018, pp. 319–324.
- [16] T. Wang, W. Yu, K. Sato, A. Moody, and K. Mohror, "An ephemeral burst-buffer file system for scientific applications," in *Proc. Int. Conf. High Perform. Comput., Netw., Storage Anal.*, 2016, pp. 807–818.
- [17] X. He et al., "HadaFS: A file system bridging the local and shared burst buffer for exascale supercomputers," in *Proc. 21st USENIX Conf. File Storage Technol.*, 2023, pp. 215–230.
- [18] W. Lv, Y. Lu, Y. Zhang, P. Duan, and J. Shu, "InfiniFS: An efficient metadata service for large-scale distributed filesystems," in *Proc. 20th USENIX Conf. File Storage Technol.*, 2022, pp. 313–328.
- [19] H. Guo, Y. Lu, W. Lv, X. Liao, S. Zeng, and J. Shu, "SingularFS: A billion-scale distributed file system using a single metadata server," in *Proc. 2023 USENIX Annu. Tech. Conf.*, 2023, pp. 915–928.
- [20] W. Cao et al., "PolarFS: An ultra-low latency and failure resilient distributed file system for shared storage cloud database," *Proc. VLDB Endowment*, vol. 11, no. 12, pp. 1849–1862, 2018.
- [21] M. Hennecke, "DAOS: A scale-out high performance storage stack for storage class memory," in *Proc. Asian Conf. Supercomputing Front.*, 2020, pp. 40–54.
- [22] S. Just, "Crimson: A new Ceph OSD for the age of persistent memory and fast NVMe storage," Santa Clara, CA: USENIX Association, Feb. 2020.
- [23] Z. Cao, S. Dong, S. Vemuri, and D. H. Du, "Characterizing, modeling, and benchmarking RocksDB key-value workloads at Facebook," in *Proc. 18th USENIX Conf. File Storage Technol.*, 2020, pp. 209–223.

- [24] M. J. Brim et al., "UnifyFS: A user-level shared file system for unified access to distributed local storage," in *Proc. 2023 IEEE Int. Parallel Distrib. Process. Symp.*, 2023, pp. 290–300.
- [25] Y. Gao et al., "When cloud storage meets RDMA," in *Proc. 18th USENIX Symp. Netw. Syst. Des. Implementation*, 2021, pp. 519–533.
- [26] Z. Yang et al., "SPDK: A development kit to build high performance storage applications," in *Proc. 2017 IEEE Int. Conf. Cloud Comput. Technol. Sci.*, 2017, pp. 154–161.
- [27] Z. Ren and A. Trivedi, "Performance characterization of modern storage stacks: POSIX I/O, libaio, SPDK, and io_uring," in *Proc. 3rd Workshop Challenges Opportunities Efficient Performant Storage Syst.*, 2023, pp. 35–45.
- [28] A. K. Paul, O. Faaland, A. Moody, E. Gonsiorowski, K. Mohror, and A. R. Butt, "Understanding HPC application I/O behavior using system level statistics," in *Proc. IEEE 27th Int. Conf. High Perform. Comput. Data Analytics*, 2020, pp. 202–211.
- [29] J. L. Bez, S. Byna, and S. Ibrahim, "I/O access patterns in HPC applications: A 360-degree survey," *ACM Comput. Surv.*, vol. 56, no. 2, pp. 1–41, 2023.
- [30] J.-W. Park, X. Huang, J.-K. Lee, and T. Hong, "I/O-signature-based feature analysis and classification of high-performance computing applications," *Cluster Comput.*, vol. 27, pp. 3219–3231, 2023.
- [31] C. Wang, K. Mohror, and M. Snir, "File system semantics requirements of HPC applications," in *Proc. 30th Int. Symp. High-Perform. Parallel Distrib. Comput.*, 2021, pp. 19–30.
- [32] B. Welch and G. Noer, "Optimizing a hybrid SSD/HDD HPC storage system based on file size distributions," in *Proc. IEEE 29th Symp. Mass Storage Syst. Technol.*, 2013, pp. 1–12.
- [33] P. Carns, S. Lang, R. Ross, M. Vilayannur, J. Kunkel, and T. Ludwig, "Small-file access in parallel file systems," in *Proc. 2009 IEEE Int. Symp. Parallel Distrib. Process.*, 2009, pp. 1–11.
- [34] Y. Wang et al., "CFS: Scaling metadata service for distributed file system via pruned scope of critical sections," in *Proc. 18th Eur. Conf. Comput. Syst.*, 2023, pp. 331–346.
- [35] S. Weil, S. A. Brandt, E. L. Miller, D. D. Long, and C. Maltzahn, "Ceph: A scalable, high-performance distributed file system," in *Proc. 7th Conf. Operating Syst. Des. Implementation*, 2006, pp. 307–320.
- [36] P. Gepner and M. F. Kowalik, "Multi-core processors: New way to achieve high system performance," in *Proc. Int. Symp. Parallel Comput. Elect. Eng.*, 2006, pp. 9–13.
- [37] S. Akhter and J. Roberts, *Multi-Core Programming*, vol. 33. Hillsboro, OR, USA: Intel Press, 2006.
- [38] B. Brank, S. Nassyr, F. Pouyan, and D. Pleiter, "Porting applications to arm-based processors," in *Proc. 2020 IEEE Int. Conf. Cluster Comput.*, 2020, pp. 559–566.
- [39] C. Guo, "RDMA in data centers: Looking back and looking forward," Keynote at APNet, 2017.
- [40] Samsung PM9A3 SSD, 2023. [Online]. Available: https://semiconductor. samsung.com/cn/ssd/datacenter-ssd/pm9a3/mzql21t9hcjr-00a07/
- [41] O. Tatebe, S. Moriwake, and Y. Oyama, "Gfarm/BB—Gfarm file system for node-local burst buffer," *J. Comput. Sci. Technol.*, vol. 35, pp. 61–71, 2020.
- [42] S. Seo et al., "Argobots: A lightweight low-level threading and tasking framework," *IEEE Trans. Parallel Distrib. Syst.*, vol. 29, no. 3, pp. 512– 526, Mar. 2018.
- [43] A fast and densely stored hashmap, 2023. [Online]. Available: https:// github.com/martinus/unordered_dense
- [44] S.-H. Chiang, R. K. Mansharamani, and M. K. Vernon, "Use of application characteristics and limited preemption for run-to-completion parallel processor scheduling policies," *ACM SIGMETRICS Perform. Eval. Rev.*, vol. 22, no. 1, pp. 33–44, 1994.
- [45] A. Dragojevi´c, D. Narayanan, M. Castro, and O. Hodson, "FaRM: Fast remote memory," in *Proc. 11th USENIX Symp. Netw. Syst. Des. Implementation*, 2014, pp. 401–414.
- [46] A. Kalia, M. Kaminsky, and D. G. Andersen, "FaSST: Fast, scalable and simple distributed transactions with two-sided(RDMA) datagram RPCs," in *Proc. 12th USENIX Symp. Operating Syst. Des. Implementation*, 2016, pp. 185–201.
- [47] S. Niazi, M. Ismail, S. Haridi, J. Dowling, S. Grohsschmiedt, and M. Ronström, "HopsFS: Scaling hierarchical file system metadata using newSQL databases," in *Proc. 15th USENIX Conf. File Storage Technol.*, 2017, pp. 89–104.
- [48] H. Greenberg, J. Bent, and G. Grider, "MDHIM: A parallel key/value framework for HPC," in *Proc. 7th USENIX Workshop Hot Top. Storage File Syst.*, 2015, Art. no. 10.

- [49] M. Ronström and J. Oreland, "Recovery principles in MySQL cluster 5.1," in *Proc. Int. Conf. Very Large Data Bases*, vol. 31, no. 2, 2005, Art. no. 1108.
- [50] K. Lu, N. Zhao, J. Wan, C. Fei, W. Zhao, and T. Deng, "TridentKV: A read-optimized LSM-tree based KV store via adaptive indexing and spaceefficient partitioning," *IEEE Trans. Parallel Distrib. Syst.*, vol. 33, no. 8, pp. 1953–1966, Aug. 2022.
- [51] J. Soumagne et al., "Mercury: Enabling remote procedure call for highperformance computing," in *Proc. 2013 IEEE Int. Conf. Cluster Comput.*, 2013, pp. 1–8.
- [52] P. Carns et al., "Mochi-hpc/mochi-margo: Argobots bindings for the Mercury RPC library," 2024. [Online]. Available: https://github.com/mochihpc/mochi-margo
- [53] A. Kalia,M. Kaminsky, and D. Andersen, "Datacenter RPCs can be general and fast," in *Proc. 16th USENIX Symp. Netw. Syst. Des. Implementation*, 2019, pp. 1–16.
- [54] K. Vaidyanathan, L. Chai, W. Huang, and D. K. Panda, "Efficient asynchronous memory copy operations on multi-core systems and I/OAT," in *Proc. 2007 IEEE Int. Conf. Cluster Comput.*, 2007, pp. 159–168.
- [55] Data plane development kit (DPDK), 2023. [Online]. Available: https: //github.com/DPDK/dpdk/
- [56] Seastar: High performance server-side application framework, 2023. [Online]. Available: https://seastar.io/message-passing/
- [57] V. Leis, A. Kemper, and T. Neumann, "The adaptive radix tree: Artful indexing for main-memory databases," in *Proc. IEEE 29th Int. Conf. Data Eng.*, 2013, pp. 38–49.
- [58] D. Ellard and J. Ledlie, "Passive NFS tracing of email and research workloads," in *Proc. 2nd USENIX Conf. File Storage Technol.*, San Francisco, CA, USA, 2003, Art. no. 15. [Online]. Available: https://www.usenix.org/ conference/fast-03/passive-nfs-tracing-email-and-research-workloads
- [59] C. Guo et al., "RDMA over commodity ethernet at scale," in *Proc. 2016 ACM SIGCOMM Conf.*, New York, NY, USA, 2016, pp. 202–215.
- [60] Z. Wang et al., "SRNIC: A scalable architecture for RDMA NICs," in *Proc. 20th USENIX Symp. Netw. Syst. Des. Implementation*, Boston, MA, USA, 2023, pp. 1–14.
- [61] BeeGFS tuning recommendations, 2024. [Online]. Available: https://doc. beegfs.io/latest/advanced_topics/benchmark.html
- [62] MDTest metadata benchmark and IOR data benchmark, 2023. [Online]. Available: https://github.com/hpc/ior
- [63] H. Shan and J. Shalf, "Using IOR to analyze the I/O performance for HPC platforms," Lawrence Berkeley National Lab.(LBNL), Berkeley, CA, USA, 2007. [Online]. Available: https://crd.lbl.gov/assets/pubs_presos/ CDS/ATG/cug07shan.pdf
- [64] J. M. Kunkel and G. S. Markomanolis, "Understanding metadata latency with MDWorkbench," in *Proc. Int. Conf. High Perform. Comput.*, R. Yokota, M. Weiland, J. Shalf, and S. Alam, Eds., Cham, Switzerland: Springer, 2018, pp. 75–88.
- [65] HACC-IO: Application centric I/O benchmark tests, 2024. [Online]. Available: https://asc.llnl.gov/coral-benchmarks
- [66] J. Borrill, L. Oliker, J. Shalf, and H. Shan, "Investigation of leading HPC I/O performance using a scientific-application derived benchmark," in *Proc. 2007 ACM/IEEE Conf. Supercomputing*, New York, NY, USA, 2007, Art. no. 10.
- [67] An adaptive radix tree for efficient indexing in main memory, 2023. [Online]. Available: https://github.com/rafaelkallis/adaptive-radix-tree
- [68] Y. Mao, E. Kohler, and R. T. Morris, "Cache craftiness for fast multicore key-value storage," in *Proc. 7th ACM Eur. Conf. Comput. Syst.*, New York, NY, USA, 2012, pp. 183–196.
- [69] N. Liu et al., "On the role of burst buffers in leadership-class storage systems," in *Proc. IEEE 28th Symp. Mass Storage Syst. Technol.*, 2012, pp. 1–11.

![](_page_16_Picture_22.png)

**Haomai Yang** received the BE degree from the Huazhong University of Science and Technology, Wuhan, China, in 2021. He is currently working toward the MS degree with the Wuhan National Laboratory for Optoelectronics, Huazhong University of Science and Technology, Wuhan, China. His current research interests include burst buffer file systems and large language model.

![](_page_16_Picture_24.png)

**Kai Lu** received the BS and PhD degrees in computer science from the Huazhong University of Science and Technology (HUST), China, in 2018 and 2023, respectively. He is currently a postdoctoral researcher with the Wuhan National Laboratory for Optoelectronics (WNLO), HUST. His research interests include computer architecture, distributed storage systems, and key-value stores.

![](_page_16_Picture_26.png)

**Wenlve Huang** received the BE degree from the Huazhong University of Science and Technology, Wuhan, China, in 2023. He is currently working toward the MS degree with the School of Computer Science and Technology, Huazhong University of Science and Technology, Wuhan, China. His current research interests include elastic block storage and parallel file systems.

![](_page_16_Picture_28.png)

**Jibin Wang** received the PhD degree in computer science from the Huazhong University of Science and Technology, Wuhan, China, in 2013. He is a professor with the Qilu University of Technology, currently mainly engaged in high-performance computing system architecture design. His research areas of interest include virtual resource scheduling, distributed storage systems, network system performance optimization, resource virtualization technology, etc.

![](_page_16_Picture_30.png)

**Yixiao Chen** received the BE degree from the Huazhong University of Science and Technology, Wuhan, China, in 2023. He is currently working toward the MS degree with the Wuhan National Laboratory for Optoelectronics, Huazhong University of Science and Technology, Wuhan, China. His current research interests include parallel file systems and RDMA network.

![](_page_16_Picture_32.png)

**Jiguang Wan** received the bachelor's degree in computer science from Zhengzhou University, China, in 1996, and the MS and PhD degrees in computer science from the Huazhong University of Science and Technology (HUST), China, in 2003 and 2007, respectively. He is currently a professor with the Wuhan National Laboratory for Optoelectronics (WNLO), HUST. His research interests include computer architecture, networked storage system, keyvalue storage system, parallel and distributed system.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:26:24 UTC from IEEE Xplore. Restrictions apply.

![](_page_17_Picture_2.png)

**Jian Zhou** received the PhD degree in computer engineering from the University of Central Florida, Orlando, FL, USA, in 2018. He joined the Wuhan National Laboratory for Optoelectronics (WNLO), Huazhong University of Science and Technology (HUST), Wuhan, China, as an associate professor in 2021. He worked as a postdoctoral fellow with the University of Central Florida from 2018 to 2020. His research interests include persistent memory and solid-state storage drive.

![](_page_17_Picture_4.png)

**Changsheng Xie** (Member, IEEE) received the BS and MS degrees in computer science from the Huazhong University of Science and Technology (HUST), China, in 1982 and 1988, respectively. He is currently a professor with the Department of Computer Engineering, Huazhong University of Science and Technology. He is also the director of the Data Storage Systems Laboratory, HUST and the deputy director of Wuhan National Laboratory for Optoelectronics (WNLO). His research interests include computer architecture, disk I/O system, networked

![](_page_17_Picture_7.png)

**Fei Wu** (Member, IEEE) received the BE and ME degrees in electrical automation, control theory, and control engineering from Wuhan Industrial University, Wuhan, China, in 1997 and 2000, respectively, and the PhD degree in computer science from the Huazhong University of Science and Technology (HUST), Wuhan, in 2005. She is currently a professor with the Wuhan National Laboratory for Optoelectronics (WNLO), HUST. Her research interests include computer architecture, nonvolatile memory, and high-performance and high-reliability storage systems.

data storage system, and digital media technology.

