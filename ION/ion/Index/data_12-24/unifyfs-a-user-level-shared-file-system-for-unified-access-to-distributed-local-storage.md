# UnifyFS: A User-level Shared File System for Unified Access to Distributed Local Storage

Michael J. Brim∗, Adam T. Moody†, Seung-Hwan Lim∗, Ross Miller∗, Swen Boehm∗,

Cameron Stanavige†, Kathryn M. Mohror†, and Sarp Oral∗

∗Oak Ridge National Laboratory, USA

Email: {brimmj, lims1, rgmiller, boehms, oralhs}@ornl.gov †Lawrence Livermore National Laboratory, USA Email: {moody20, stanavige1, mohror1}@llnl.gov

*Abstract*—We introduce UnifyFS, a user-level file system that aggregates node-local storage tiers available on high performance computing (HPC) systems and makes them available to HPC applications under a unified namespace. UnifyFS employs transparent I/O interception, so it does not require changes to application code and is compatible with commonly used HPC I/O libraries. The design of UnifyFS supports the predominant HPC I/O workloads and is optimized for bulk-synchronous I/O patterns. Furthermore, UnifyFS provides customizable file system semantics to flexibly adapt its behavior for diverse I/O workloads and storage devices. In this paper, we discuss the unique design goals and architecture of UnifyFS and evaluate its performance on a leadership-class HPC system. In our experimental results, we demonstrate that UnifyFS exhibits excellent scaling performance for write operations and can improve the performance of application checkpoint operations by as much as 3× versus a tuned configuration.

*Index Terms*—Distributed file systems, Parallel I/O, Parallel systems, Storage hierarchies, Storage devices

### I. INTRODUCTION

Scientific applications on high performance computing (HPC) systems are producing and consuming data at everincreasing rates. Applications are being run at larger scales that produce larger aggregate data, and the rate at which data is produced is increasing due to advances in compute node technologies that shorten time step computation cycles between data products. The increasing file sizes and access rates result in unacceptably high I/O times for applications due to contention for the shared parallel file system (PFS). To alleviate the PFS I/O bottleneck, system designers have introduced new tiers of storage that can provide higher I/O performance. For example, Summit at Oak Ridge National Laboratory uses node-local storage (NLS) to augment the parallel file system [1] and the El Capitan system at Lawrence Livermore National Laboratory will pioneer a near-node-local storage capability [2]. The new tiers of storage offer many

Notice: This manuscript has been authored by UT-Battelle, LLC, under contract DE-AC05-00OR22725 with the US Department of Energy (DOE). The US government retains and the publisher, by accepting the article for publication, acknowledges that the US government retains a nonexclusive, paid-up, irrevocable, worldwide license to publish or reproduce the published form of this manuscript, or allow others to do so, for US government purposes. DOE will provide public access to these results of federally sponsored research in accordance with the DOE Public Access Plan (http://energy.gov/downloads/doe-public-access-plan).

advantages for I/O performance over parallel file systems local I/O operations achieve consistent bandwidth and latency due to reduced contention, and I/O bandwidth scales with the number of nodes in the job [3]. However, these distributed, independent local storage tiers are challenging to use because they do not offer a shared file namespace which is required for many HPC application I/O patterns.

Furthermore, most HPC file systems adhere to the conservative consistency semantics of the POSIX I/O specification [4], which introduces high I/O overheads because file systems must ensure that the outcome of concurrent file operations reflect a consistent sequential ordering and that writes are immediately visible to all processes upon completion. However, POSIX I/O consistency is rarely necessary for HPC [5]. Weaker semantics are typically sufficient for HPC parallel I/O because concurrent file accesses by processes are often disjoint such that no two processes access the same region of a file at the same time. Unfortunately, existing file systems do not provide capabilities for trading less stringent semantics for improved I/O performance.

To address these limitations we introduce UnifyFS [6], [7], an ephemeral, user-level file system that provides a unified view over distributed, node-local storage within a single HPC batch job. UnifyFS makes applications' use of local storage tiers as easy as using parallel file systems. Since UnifyFS transparently intercepts application I/O, applications typically need only to link with its client library and modify their file paths to use UnifyFS. This also allows applications to benefit from continued improvements to I/O libraries and middleware by avoiding application and library code modifications. When using UnifyFS, users can expect to see the same benefits from their optimized applications and libraries, with the additional benefits to scalability from reduced contention. In addition to being easy to use, UnifyFS provides high performance because it is specialized for the bursty, bulk-synchronous I/O patterns that are common in HPC workloads. Furthermore, UnifyFS provides user-customizable semantics to flexibly adapt its behavior to further improve performance.

Our contributions in this paper are as follows:

<sup>1)</sup> an investigation of the potential benefits and tradeoffs of user-customizable ephemeral file system behavior based on required application I/O semantics;

DOI 10.1109/IPDPS54959.2023.00037

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 21:46:36 UTC from IEEE Xplore. Restrictions apply.

- 2) a scalable data and metadata management architecture design that supports such flexible customization;
- 3) an exploration of the solution space for customization and I/O interception capabilities that do not require application source code modifications for a wide variety of common HPC I/O usage models; and
- 4) a comprehensive evaluation of UnifyFS performance using the IOR benchmark and the Flash-X astrophysics application on two production HPC systems.

#### II. UNIFYFS OVERVIEW

The design of UnifyFS is novel because it represents a departure from the status quo for HPC file systems. Our goal is to support the I/O needs of HPC applications while fully exploiting the isolation and performance benefits of nodelocal storage devices. The flexible semantics of UnifyFS allow HPC users to tune its behavior to support the exact needs of applications, thus avoiding costly overheads in maintaining POSIX I/O semantics.

UnifyFS is an ephemeral, user-level file system for HPC systems. It is ephemeral because the lifespan of the file system is limited to a single job allocation. The servers that host UnifyFS are not started until the job allocation has started, and terminate when the job ends. Data written to UnifyFS is removed when the servers are terminated. To persist data beyond the lifespan of UnifyFS, users must explicitly copy data from UnifyFS to another persistent storage location before terminating the servers. UnifyFS is user-level because it can be configured and run by any regular user; no privileged system account is required. An instance of UnifyFS has the same permissions and access to system resources as any other user application within the job. UnifyFS is not designed to replace the HPC system's shared file system like Lustre or GPFS. Rather, UnifyFS is an additional file system that can be used within a job for higher performance.

Each user of UnifyFS may choose to enable different features and optimizations, based on the file system semantics requirements of the target application. These custom configurations can improve performance at the cost of reducing generality. UnifyFS is not POSIX-compliant and deviates from the standard in cases where one can gain significant performance for common HPC parallel I/O patterns. For example, by default UnifyFS does not make the result of a write operation on a file immediately visible to all readers. Instead, UnifyFS meets the consistency requirements of typical HPC applications using *commit consistency semantics* [5]. UnifyFS requires a process that writes data to first synchronize with the file system and then with other processes before that data is guaranteed to be visible to those other processes. This explicit consistency model enables faster write performance to shared files on distributed systems, since data from many writes can be buffered locally at a client before informing the file system servers. Because UnifyFS executes at user-level within a job allocation and supports a single user at a time, it can also safely relax requirements such as checking file permissions and consistency of the file namespace hierarchy, which can reduce metadata management overheads. Finally, since the use of UnifyFS is entirely optional, it does not need to support all applications that might run on the system. This contrasts with the the parallel file system that must support the I/O behavior of all applications and users on the system.

### *A. UnifyFS Write Semantics*

UnifyFS specifically aims to improve performance for parallel applications that write shared files, where processes concurrently write to the same file. Shared files are desirable because they reduce the file count of large-scale HPC applications, yet they present a write pattern that is difficult to support efficiently under POSIX I/O. The POSIX requirement to make write operations immediately visible holds for any process that can access the file, even if it is running on a different compute node than the process that wrote the data. This forces POSIXcompliant file systems to internally lock regions of the file during write operations, which can degrade overall application write performance. However, most HPC applications do not require data to be visible after each write operation [5], even when directly using POSIX I/O.

Other I/O standards designed for HPC require the application to declare when the written data should be made visible. For instance, MPI-IO requires the application to call MPI_File_sync before data written by a process can be read by other processes. MPI-IO applications may issue multiple write operations before making this synchronization call, and the MPI library can buffer the written data at clients until the synchronization. By reducing application synchronization with the file system, the file system can achieve higher write performance.

Based on application needs, users can configure UnifyFS to use any of three different write modes: *read-after-write* (RAW) which makes data visible after each write (like POSIX); *read-after-sync* (RAS) which makes data visible after an I/O synchronization call like fsync or MPI_File_sync; and *read-after-laminate* (RAL) where data is only readable after an explicit *laminate* operation.

The RAW mode enables applications that require POSIX I/O write semantics to use UnifyFS. No changes to the application I/O logic are required, but it offers lower performance due to increased synchronization overhead. With RAS, data written by a process is not visible to other processes until the next application synchronization call. This mode is a natural fit for applications using MPI-IO. Again, no application changes are needed to use this mode, and the additional buffering significantly improves write performance. The RAL mode allows for the highest performance, but it is the least general as written data is not visible to other processes until the file has been laminated. To use this property, an application or I/O library explicitly invokes the UnifyFS *laminate* operation which puts the file into a permanent read-only state where the file may be deleted but may not be modified. To avoid application modifications, UnifyFS can be configured to implicitly invoke the laminate operation during common I/O calls like chmod or close.

# *B. UnifyFS Read Semantics*

UnifyFS also enables users to configure the behavior of read operations to optimize application performance. In the general case, UnifyFS supports applications where different processes write to the same offset within a file. During a read operation, the UnifyFS servers coordinate to locate and return the most recent data written to the requested region. The communication to find and read remote data across the network can be costly to read performance. However, HPC applications do not typically overwrite bytes within a file [5]. There are many applications in which each byte within a file is written once. Additionally, there are common cases like checkpoint/restart workloads in which the process rank in a parallel job that wrote data to a file is the same rank to read the data back.

For applications that meet these two conditions, users may configure UnifyFS to cache file metadata for faster retrieval during read operations. When enabled, UnifyFS caches file metadata locally to service reads for that data without having to communicate with remote servers, which drastically improves read performance. There are two variants of this mode: *client caching* and *server caching*. Client caching is useful in applications where no two processes write to the same offset. In this mode, UnifyFS may cache metadata local to the process so that reads can be serviced fully in the client without contacting any server. Server caching is useful in applications where only processes on the same node write to the same offset. In this case, the local UnifyFS server can fully service a client read without contacting remote servers. It is important to only enable these modes when one is certain about the application behavior. If one enables either of these modes for an application where remote clients overwrite a file region, then the data returned by a read operation is undefined.

Finally, applications can boost read performance with lamination, which allows UnifyFS to cache data and metadata more aggressively. Currently, metadata detailing the location of all file data is broadcast to all servers, which reduces data lookup costs during reads. This optimization is useful even for applications that require overwrite support.

# III. UNIFYFS ARCHITECTURE

UnifyFS employs a client-server architecture with one server process deployed per node in a job allocation. Clientserver and server-server communications utilize Margo [8], which integrates Argobots [9] lightweight threading with the HPC remote procedure call (RPC) capabilities of Mercury [10]. To enable scalable communication for large jobs with many server processes, UnifyFS uses tree-based topologies to communicate among servers where possible. For instance, file laminate, truncate, and unlink operations are broadcast to all servers using binary trees that are rooted at the owner server. The cost for such operations scales logarithmically with server count. The servers must be launched and interconnected prior to servicing application client requests. UnifyFS provides a utility program for use within job scripts that works with the system resource manager to start and terminate the servers. The same utility program provides support for optional staging of files into UnifyFS at the beginning of a job or staging files out of UnifyFS at the end of a job.

Application clients (i.e., processes linked with the UnifyFS client library) on a node interact with only their local server. The client library uses function interposition to intercept I/O system calls (e.g., open, read, write, and close) in the application. Users of UnifyFS specify a mountpoint prefix path to serve as the root of its namespace. To determine when a target file resides within UnifyFS, the absolute path of the file is computed and compared to the prefix path. For files not residing within the UnifyFS namespace, the client library simply passes the request on to the original I/O function. When the target file is located within UnifyFS, the library handles the I/O operation directly or by making RPC requests to the local server. The server either handles the request locally or forwards the request in the form of RPCs to the appropriate remote server(s). When the client's request is completed at the local server, including processing of any remote RPC responses, the request completion status and any applicable data or metadata are returned to the client library.

UnifyFS supports three different methods of function interposition: Gotcha [11]; dynamic library preloading (i.e., LD_PRELOAD); and static linker wrapping. Gotcha is the default method used by UnifyFS because its method of interposition via the process Global Offset Table (GOT) works even when additional libraries are dynamically loaded into the application at runtime, as is the case for some MPI-IO implementations. If Gotcha is not available on a given system, dynamic preloading or static linker wrapping may be used.

Figure 1 shows the data and metadata management architecture of UnifyFS. To support efficient parallel writes to shared files, UnifyFS implements a log-based storage scheme where all data written by clients is stored locally. UnifyFS is not tailored to any particular NLS technology, and uses only widely-available methods for local data storage to ensure portability. UnifyFS supports two forms of local storage, shared memory and local file. The client chooses one or both forms via configuration settings.

For file-based storage, the configuration provides the name of a directory on a local file system in which to create perclient data storage files. A typical file storage location is within the file system mountpoint for compute NLS, though other locations can be used such as a memory-backed file system like tmpfs. Each client process allocates a fixed-size data storage region within each selected form of local storage. The configuration specifies each data region's size and the data chunk size that is used to logically slice the storage region. A chunk usage bitmap is maintained at the beginning of each data storage region to track allocated and free chunks within the region. The client library exchanges information about its local storage regions with the local server when it mounts UnifyFS. The server then attaches to the shared memory or opens the local file to access the data.

As the client writes data to files in UnifyFS, the library allocates contiguous chunks from the local storage and copies the data from the application memory buffer to the allocated

![](_page_3_Figure_0.png)

Fig. 1: Data and Metadata Storage in UnifyFS

chunks. For shared memory storage, memcpy() is used for data copies, while file storage uses pwrite(). When both shared memory and file storage are used, the storage regions are logically combined and treated as one contiguous local storage region. The client library first allocates from shared memory, and when that space is exhausted, chunks are allocated from file storage. Because storage chunks are allocated in a sequential fashion, I/O accesses to file storage are often sequential as well. When a client writes to many files concurrently, the data will be interleaved in the local storage.

UnifyFS uses *file extent* metadata to track the local storage data chunks associated with each file. A file extent is a contiguous set of bytes within the file, represented as a starting logical file offset and extent length. This extent metadata is organized as per-file red-black trees of extent structures. The extent structure records the file extent as well as the corresponding data chunks, which are represented by their offset within a particular local data storage region identified by server rank and a unique id assigned to the client. The client library and servers also collectively maintain general metadata for each object in the UnifyFS namespace. Currently, the supported object types are regular files and directories. The metadata associates a globally unique identifier with properties like the object type, permission bits, lamination status, file size, and any timestamps. The *file owner* is the server who maintains the global view of extent and object metadata for a file before lamination. The owner is selected by hashing the target file path to a particular server rank. To create or delete an object, an RPC is sent to the owner server. For efficiency, the client library and non-owner servers cache metadata for use between synchronization points.

Given that the semantics of UnifyFS require explicit synchronization to expose newly written data, the client maintains a tree of unsynced extents. Each client write operation either creates a new extent structure or extends an existing one in the unsynced extents tree. Extension is used when the logical file offsets for two writes are consecutive (i.e., the offset of the second write is equal to the first write offset plus its length) and the associated chunk storage locations are also contiguous. If a write overlaps with existing extents, the tree ensures that the affected extents are either truncated for partial overlaps or deleted for full overlaps. At various synchronization points, like file fsync, ftruncate, and close calls, the client serializes the extent tree into a write log in shared memory and issues a sync RPC to its local server. The server then merges those write extents into its own per-file extent tree that contains all synced extents from local clients, and then forwards the newly synced extents on to the owner server (in the case the local server is not the owner). When the owner receives the new extents, it merges them with its global extent tree for the file and updates the file's size in the global metadata if necessary. Upon lamination of a file, the owner server broadcasts the finalized file metadata and the full set of extents to all other servers, who replace their local metadata.

When an application issues a read operation for a UnifyFS file, the client library issues a read RPC to its local server. The server first looks up any extents corresponding to the byte range of the read extent. If the file is not laminated, the server must query the owner server for the file. For laminated files, the server can use its local copy of the extent tree. Once the local server has identified all associated extents, it issues server read requests for the relevant portion of each extent. For local data, the server directly reads the file data from the storage locations. To fetch remote data, the server issues a single remote read RPC per server that contains all the requested extents located on that server. Remote servers service the incoming read requests by aggregating the data copied from each extent's storage location into a single indexed buffer and returning the buffer to the local server via another RPC. As data responses arrive, the local server streams the data back to the client library of the application process via shared memory and RPC, which copies the data segments into the application buffer. Once all response data has been processed, the client library returns from the read I/O operation.

#### IV. EVALUATION

#### *A. Experimental Environments*

Summit is a large-scale HPC system located at the Oak Ridge Leadership Computing Facility (OLCF). We selected Summit for our experimental evaluation of UnifyFS due to its use of NLS and its connection to Alpine, the OLCF center-wide file system. Alpine [1] is an IBM Spectrum Scale parallel file system providing 250 petabytes of scratch storage capacity and peak sequential I/O bandwidth of 2.5 TB/s. A Summit compute node contains a 1.6 TB NVMe storage device providing peak write bandwidth of 2.1 GB/sec (2.0 GiB/sec) and read bandwidth of 5.5 GB/sec (5.1 GiB/sec) [1]. Each node also contains two IBM POWER9 22-core CPUs, with 256 GB of DDR4 RAM per CPU, and each CPU is connected to three NVIDIA V100 GPUs, with 16 GB of HBM2 per GPU. Summit compute nodes are networked together and to Alpine using a Mellanox EDR Infiniband network. Each Summit node has a 12.5 GB/sec maximum data transfer rate to the Alpine servers over the network. Summit provides IBM Spectrum MPI, which is an enhanced version of OpenMPI that integrates the Infiniband network and NVIDIA GPUs and uses the ROMIO MPI-IO implementation.

Crusher is a testbed HPC system at the OLCF that provides early access to the software and hardware environment for the upcoming Frontier exascale system. Similar to Summit, Crusher uses Alpine for its parallel file system and has compute nodes with NLS devices. Each of Crusher's 192 nodes contains a single 64-core AMD EPYC x86-64 CPU with 512 GB of DDR4 RAM, and four AMD MI250X GPUs each with 128 GB of HBM2. Each MI250X GPU contains two Graphics Compute Dies (GCD), for a total of eight programmable GPU devices per node. The NLS consists of two 1.92 TB NVMe devices per node, each with peak write bandwidth of 2.0 GB/sec and read bandwidth of 5.5 GB/sec. The nodelocal devices are combined within a single logical volume that stripes data across both devices. Crusher compute nodes are networked together using an HPE Slingshot network, with each node having 800 Gbps of injection bandwidth. Crusher provides Cray MPICH, which integrates the Slingshot network and the AMD GPUs and uses ROMIO for MPI-IO.

# *B. IOR Benchmark Evaluation on OLCF Summit*

We used the IOR1 benchmark to evaluate the functionality and performance of UnifyFS using a variety of widely-used HPC I/O methods. Specifically, we used IOR version 3.3 with minor modifications to the configuration and build process to TABLE I: IOR Write Bandwidth (GiB/s) for Shared POSIX File on Summit Node-local Storage (6 processes, 1 GiB per process)

| File | Transfer Size |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| Storage | 64 KiB | 1 MiB | 4 MiB | 8 MiB | 16 MiB |
| xfs-nvm | 1.8 ± 0.0 | 1.8 ± 0.0 | 1.8 ± 0.0 | 1.7 ± 0.0 | 1.7 ± 0.0 |
| UFS-nvm | 2.0 ± 0.0 | 2.0 ± 0.0 | 2.0 ± 0.0 | 2.0 ± 0.0 | 2.0 ± 0.0 |
| UFS-shm | 51.1 ± 0.6 51.7 ± 4.2 47.0 ± 2.7 34.8 ± 1.4 34.8 ± 1.4 |  |  |  |  |
|  | tmpfs-mem 14.3 ± 0.1 14.3 ± 0.0 11.7 ± 0.0 10.6 ± 0.0 10.3 ± 0.0 |  |  |  |  |

optionally link against the UnifyFS client library2. For each IOR experiment in this subsection, we used a single job to compare all tested configurations for a given Summit node count. This ensures all configurations use the same set of allocated nodes and experience the same conditions when accessing shared resources such as the HPC network and parallel file system. We executed each IOR configuration three times, with each run using five iterations on different files (i.e., with options '-m -i 5'). Within a job, we interleave the IOR runs using a loop that executes each compared configuration once per loop iteration. We report the IOR results from the best performing run for each configuration. For all IOR runs, UnifyFS uses the IOR transfer size as its chunk size for log-based storage.

*1) Baseline Shared-file Write Performance for Node-local Storage:* First, we investigated the baseline write performance on one Summit node using various types of local storage. Table I shows the mean write bandwidth with standard deviation for six processes writing 1 GiB each to a shared POSIX file using various IOR transfer sizes. UnifyFS is configured to use its default read-after-sync (RAS) mode. For node-local NVM, we compare direct use of the xfs file system (xfs-nvm) with UnifyFS (UnifyFS-nvm), which stores its data files in an xfs file system directory. UnifyFS is able to fully exploit the available write bandwidth, while xfs-nvm cannot, likely due to POSIX file sharing overhead. UnifyFS avoids sharing overhead by using per-client data storage files. For memorybased local storage, we compare the tmpfs file system (tmpfs-mem) versus UnifyFS configured to only use shared memory (UnifyFS-shm). The UnifyFS-shm results show the additional write performance available when using shared memory for local data storage and that it significantly outperforms tmpfs, by as much as 4×. Use of tmpfs involves data copies between user and kernel space, while UnifyFS-shm only requires user-space memory copies. Also, adhering to POSIX file sharing semantics may limit tmpfs performance for multiple processes.

*2) Write and Read Performance and Scalability for POSIX I/O and MPI-IO:* The remaining IOR experiments evaluate UnifyFS performance scalability across multiple nodes on shared files using POSIX I/O and MPI-IO. We execute IOR to first write a shared file, including a file sync (i.e., with options '-w -e'). Then, we execute IOR again to read back

<sup>1</sup>hpc/ior: IOR and mdtest: https://github.com/hpc/ior

<sup>2</sup>https://github.com/MichaelBrim/ior/tree/unifyfs-support

![](_page_5_Figure_0.png)

Fig. 2: IOR Shared File Bandwidth using POSIX I/O, MPI-IO independent, and MPI-IO collective APIs on Alpine PFS and UnifyFS (Summit, 6 ppn, 1 GiB per process)

the previously written file. For these experiments, UnifyFS uses only the node-local NVM for data storage.

Figure 2 shows the mean write and read bandwidth with standard deviation for the Alpine parallel file system (PFS) and UnifyFS for POSIX, MPI-IO independent, and MPI-IO collective. For MPI-IO tests, we use the default configuration of MPI-IO provided by Summit and intercept the POSIX I/O calls made inside the ROMIO ADIO layer. These tests use six processes per node (ppn), a transfer size of 16 MiB, and a single 1 GiB segment per process. The total size of each shared file can be computed as number of processes × IOR segment size. UnifyFS uses its default RAS mode.

Write performance (see Figure 2a) for UnifyFS compares favorably to using the PFS with all I/O methods and exhibits much less variability as indicated by the whiskers that show standard deviation. With POSIX I/O, UnifyFS performance scales nearly linearly at the expected 2 GiB/sec rate per node, while the PFS rate peaks at around 80 GiB/sec with 16 nodes. MPI-IO shows much better scaling behavior than POSIX when using the PFS, but still exhibits large variability. At smaller node counts, UnifyFS performance with MPI-IO tracks that seen with POSIX, but trails MPI-IO on PFS. However, at larger scales from 128 nodes and up we observe that UnifyFS clearly provides a performance benefit over MPI-IO on PFS for both independent and collective writes, as much as 1.7× and 6.5×, respectively, at 512 nodes.

Read performance (see Figure 2b) for UnifyFS is poor compared to using the PFS with all I/O methods, but still exhibits much less variability. The PFS results appear to benefit from temporal caching of the previously written data in either the local node file buffer cache or in the Alpine storage servers. Reads in UnifyFS are performed by the server process on the node where the data was written. Although the server is multi-threaded to allow simultaneous request processing for multiple clients, it still represents a potential bottleneck in read processing. For POSIX I/O and MPI-IO independent runs, all data is written on the local node and only local reads are required, resulting in per-node read bandwidth of roughly 1.8 GiB/sec. However, the read performance peaks near 185 GiB/sec for 128 nodes and then decreases at larger scales. This poor read scaling behavior is primarily caused by the need to query the owner server that maintains the file metadata to determine extent locations for each read operation, and the number of these requests increases linearly with the node count. As a result, the owner server processing of these extent lookup requests becomes a bottleneck. With MPI-IO collective mode data is aggregated to a subset of ranks before writing, which further reduces UnifyFS read performance due to the need to perform remote server read operations.

*3) Impacts on Write Performance for Varied Synchronization Behaviors:* The results in Figure 2a represent UnifyFS write behavior in its default RAS configuration, where data is made available for remote processes through an explicit synchronization operation that includes an underlying system call to persist the data to the NVM. To further explore the write performance of UnifyFS, we conducted a series of experiments where we vary the synchronization behaviors. These experiments again use six processes per Summit node, and 1 GiB of data written per process. For each tested configuration, we use two IOR block and transfer size combinations, one with 4 MiB transfers and 256 MiB blocks and another with 16 MiB transfers and 1 GiB blocks, to show the impact of increasing the number of write extents. At each node scale, we report the average IOR time spent in the open, write, and close phases, as well as the average total elapsed time. Note that due to its parallel nature, IOR calculates the time durations using the minimum start and maximum end time across all processes. As such, these phases may overlap across processes and the total time is not a strict summation of these timings. It is also important to note that IOR includes synchronization

TABLE II: IOR Shared POSIX File Write Behavior without Data Persistence (Summit, 6 ppn, 1 GiB per process)

| (a) Configuration 1 - no sync, no data persistence |
| --- |

|  |  |  | IOR Parameters Nodes Extents open (s) write (s) close (s) total (s) |  |  |  | GiB/s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T = 4 MiB, | 8 | 192 | 0.046 | 0.165 | 0.083 | 0.166 | 289.7 |
| B = 256 MiB | 64 | 1536 | 0.050 | 0.215 | 0.136 | 0.215 1782.2 |  |
|  | 256 | 6144 | 0.510 | 0.585 | 0.516 | 0.596 2577.6 |  |
| T = 16 MiB, | 8 | 48 | 0.037 | 0.200 | 0.071 | 0.201 | 239.3 |
| B = 1 GiB | 64 | 384 | 0.046 | 0.264 | 0.149 | 0.275 1398.4 |  |
|  | 256 | 1536 | 0.274 | 0.431 | 0.334 | 0.449 3417.4 |  |

(b) Configuration 2 - sync at end, no data persistence

|  |  |  | IOR Parameters Nodes Extents open (s) write (s) close (s) total (s) |  |  |  | GiB/s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T = 4 MiB, | 8 | 192 | 0.051 | 0.161 | 0.080 | 0.161 | 297.6 |
| B = 256 MiB | 64 | 1536 | 0.055 | 0.211 | 0.130 | 0.211 1819.8 |  |
|  | 256 | 6144 | 0.269 | 0.416 | 0.293 | 0.416 3691.4 |  |
| T = 16 MiB, | 8 | 48 | 0.038 | 0.200 | 0.071 | 0.200 | 240.2 |
| B = 1 GiB | 64 | 384 | 0.047 | 0.257 | 0.126 | 0.257 1495.6 |  |
|  | 256 | 1536 | 0.075 | 0.342 | 0.219 | 0.342 4488.6 |  |

| (c) Configuration 3 - sync per write, no data persistence |
| --- |

|  |  |  | IOR Parameters Nodes Extents open (s) write (s) close (s) total (s) GiB/s |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| T = 4 MiB, | 8 | 12288 | 0.031 | 0.639 | 0.217 | 0.639 75.2 |
| B = 256 MiB | 64 | 98304 | 0.056 | 4.630 | 4.012 | 4.630 82.9 |
|  | 256 | 393216 | 0.284 | 34.382 | 33.924 34.382 | 44.7 |
| T = 16 MiB, | 8 | 3072 | 0.030 | 0.299 | 0.123 | 0.299 160.6 |
| B = 1 GiB | 64 | 24576 | 0.035 | 1.214 | 0.965 | 1.214 316.3 |
|  | 256 | 98304 | 0.214 | 8.718 | 8.464 | 8.718 176.2 |

TABLE III: IOR Shared POSIX File Write Behavior with Data Persistence (Summit, 6 ppn, 1 GiB per process)

(a) Configuration 1 - sync at end, persist at sync

|  |  |  | IOR Parameters Nodes Extents open (s) write (s) close (s) total (s) GiB/s |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| T = 4 MiB, | 8 | 192 | 0.044 | 3.104 | 1.315 | 3.104 15.5 |
| B = 256 MiB | 64 | 1536 | 0.122 | 3.922 | 1.924 | 3.922 97.9 |
|  | 256 | 6144 | 0.371 | 3.554 | 1.868 | 3.554 432.2 |
| T = 16 MiB, | 8 | 48 | 0.072 | 3.110 | 1.312 | 3.110 15.4 |
| B = 1 GiB | 64 | 384 | 0.052 | 3.902 | 2.166 | 3.902 98.4 |
|  | 256 | 1536 | 0.071 | 3.716 | 2.274 | 3.716 413.3 |

(b) Configuration 2 - sync per write, persist at sync

|  |  |  | IOR Parameters Nodes Extents open (s) write (s) close (s) total (s) GiB/s |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| T = 4 MiB, | 8 | 12288 | 0.020 | 4.328 | 0.800 | 4.330 11.1 |
| B = 256 MiB | 64 | 98304 | 0.042 | 6.034 | 2.694 | 6.034 63.6 |
|  | 256 | 393216 | 0.213 | 35.020 | 31.812 35.020 | 43.9 |
| T = 16 MiB, | 8 | 3072 | 0.018 | 3.976 | 0.488 | 3.976 12.1 |
| B = 1 GiB | 64 | 24576 | 0.038 | 3.644 | 0.747 | 3.644 105.4 |
|  | 256 | 98304 | 0.199 | 9.400 | 6.322 | 9.400 163.4 |

time within its reported write phase time. We also provide the effective average write bandwidth (GiB/s) that is derived as total f ile size/total time.

Table II provides insight into the write behavior when we disable data persistence within UnifyFS, which skips the internal fsync system calls for the data storage files on NVM. With persistence disabled, application-level synchronization operations only result in exchanging the extent metatdata with the local and owner servers. We test three configurations that vary the time when synchronization occurs using the associated IOR options. The first configuration (Table IIa) disables the application synchronization operation entirely by omitting the IOR '-e' option, which results in the extent metadata being sent to the server during the close phase. The second configuration (Table IIb) synchronizes at the end of the IOR write phase using the IOR '-e' option. The third configuration (Table IIc) synchronizes after each IOR write operation using the IOR '-Y' option, which is effectively the same as enabling the UnifyFS read-after-write (RAW) mode. For the first two configurations, the UnifyFS client library consolidates contiguous write extents, so each process ends up syncing one extent per block. In the third configuration, each write transfer extent is synchronized, resulting in a significantly larger number of extents (i.e., 64 extents per block). Our expectation was that the first and second configurations should provide roughly the same write performance, but our results showed that the second configuration performs better. We noted that at 256 nodes the first configuration spends more time in the open phase, which may be due to intermittent network congestion delaying metadata lookup RPCs. As expected, the first configuration has a greater proportion of its time in the close phase where extents are synchronized. The third configuration reveals the serializing effects of syncing after every write operation, which is limited by RPC processing speed at the file owner server and exacerbated at large scales due to the large number of extents. At 64 and 256 nodes for example, the write phase time and total time for the IOR runs with 4× as many extents are roughly 4× longer. We also verified that the third configuration, with application-level synchronization after each write operation, provides the same performance behavior as configuring UnifyFS in RAW mode.

Table III shows the write behavior of UnifyFS when we enable data persistence to the NVM, which is the default configuration for UnifyFS. The first configuration (Table IIIa) synchronizes at the end of the IOR write phase. The second configuration (Table IIIb) synchronizes after each IOR write operation. The additional cost of data persistence is more noticeable for the "sync at end" configurations (Table IIb and Table IIIa), where the time to persist 6 GiB of data per node (roughly 3 seconds) dominates the write phase and total time. For the "sync per write" configurations (Table IIc and Table IIIb), data persistence overhead is amortized over many synchronization operations and overall time is dominated by extent metadata management.

*4) Impacts on Read Performance from Extent Metadata Caching:* Next, we evaluate the additional read performance obtained when enabling the optional UnifyFS client or server caching of extent metadata or when using file lamination. Two read patterns are used to show the benefits presented in Figure 3. The first is local reads (Figure 3a), where the rank that wrote the data is the same that reads it. This mimics the common I/O pattern of a process reading checkpoint data for restart. The second, rank-reordered reads (Figure 3b) where a different rank does the read, is a more challenging pattern not commonly seen in HPC applications, but included for completeness. For the second pattern, we use the IOR default reordering where rank N+1 reads the data written by rank N. In our Summit jobs, ranks are packed so that six contiguous ranks are co-located on each node. The reordering thus results in one rank per node reading data from a remote node, while the other five ranks read local data.

For reads of local data, server caching (UnifyFS-server) and lamination (UnifyFS-laminated) both avoid RPCs to the file owner to find the locations of the extents, and the performance benefits versus default read performance (UnifyFS-default) increase with larger scales. Client caching (UnifyFS-client) greatly improves read performance by bypassing the local server during the read operation, allowing bandwidth to scale linearly with the node count and providing 8× the PFS bandwidth at 256 nodes.

With read reordering, we first notice that UnifyFS default read performance drops roughly 50% versus local reads, showing the performance penalty of remote data access. In contrast, Alpine appears to provide consistent performance for both local and reordered reads. Server extent caching benefits are also minimal for reordered reads, as the bandwidth is rate limited by the slower remote data access times. However, file lamination improves read performance by eliminating remote metadata queries and shows better scaling behavior than the PFS. We speculate that at larger node counts, reading laminated files from UnifyFS will outperform PFS reads.

## *C. Flash-X Application Evaluation on OLCF Summit*

In order to show the benefits of UnifyFS on a real application, we used the Flash-X astrophysics simulation with six processes per node, its typical run configuration on Summit. The specific configuration we used is called FLASH-IO. It simulates the application's I/O behavior when writing shared checkpoint files in HDF5 format, while skipping the computationally expensive simulation. The checkpoint file size increases linearly with the number of application processes. On a single node, each checkpoint is approximately 36 GB. Flash-X contains timers that measure the time to write each checkpoint file and reports the times upon completion. We ran Flash-X five times at each job size up to 128 nodes, and use the median checkpoint time along with the total size of the shared checkpoint file to derive the achieved write bandwidth. At 128 nodes, each checkpoint is around 4.5 TB.

Our initial results comparing Flash-X checkpointing performance on Alpine with UnifyFS showed poor overall write bandwidth that was much lower than expected for both cases. We then investigated the I/O behavior in more detail using the Darshan and Recorder I/O profiling tools. The performance bottleneck was identified as excessive calls to H5Fflush, one for every write to the checkpoint file. After consultation with the HDF5 and application developers, it was concluded that these flush operations were not required for correct application behavior. The HDF5 developers also suggested that recent library improvements may benefit Flash-X. As shown in Figure 4, we compared four configurations: (1) baseline PFS performance using the default HDF5 v1.10.7 on Summit and an unmodified Flash-X (PFS-1.10.7), (2)

**(a) IOR Local Read Bandwidth - POSIX Shared File**

![](_page_7_Figure_7.png)

# Nodes (6 processes per node) **(b) IOR Reorder (N+1) Read Bandwidth - POSIX Shared File**

![](_page_7_Figure_9.png)

Fig. 3: IOR Shared POSIX File Read Bandwidth with Optional UnifyFS Extent Caching or Lamination (Summit, 6 ppn)

![](_page_7_Figure_11.png)

Fig. 4: Flash-X Shared Checkpoint File Write Bandwidth on Alpine and UnifyFS (Summit, 6 ppn)

PFS performance with the tuned Flash-X version that eliminates the redundant flushes (PFS-1.10.7-tuned), (3) PFS performance with the latest HDF5 v1.12.1 and the tuned application (PFS-1.12.1-tuned), and (4) UnifyFS performance with the latest HDF5 version and the tuned application (UnifyFS-1.12.1-tuned).

We observe that UnifyFS shows better scalability character-

istics than Alpine, which suffers due to network and storage resource contention that increases with larger jobs. In contrast, UnifyFS provides consistent performance that scales nearly linearly by leveraging the NLS and reducing interference from concurrent workloads. At 128 nodes, UnifyFS performs 3× better than the tuned application and latest HDF5 on Alpine, and 53× better than the baseline unmodified application on Alpine with the default HDF5.

### *D. GekkoFS Comparison on OLCF Crusher*

Similar to UnifyFS, GekkoFS [12] is a user-level ephemeral distributed file system that enables a unified view over NLS devices within a job. Both systems use the same underlying communication libraries (i.e., Margo and Mercury), employ a single server process per compute node, and use a data chunking technique for managing storage and locating file data. It is useful to compare UnifyFS versus GekkoFS to highlight the impact of their unique design choices for data placement. Unlike UnifyFS where clients write directly to local storage and data is kept local to the node, GekkoFS forwards all write operations to local or remote servers based on a wide-striping technique that is designed to help balance the distribution of data chunks across all nodes.

Since the I/O interception library used by GekkoFS only supports x86-64 systems, we used OLCF Crusher to compare the two file systems. GekkoFS v0.9.0 was used for the comparison with its recommended versions of software dependencies. Both GekkoFS and UnifyFS used the same versions of Margo and Mercury and the same underlying system-provided libfabric.

IOR is used to compare the write and read performance of the two file systems on shared files using POSIX I/O and MPI-IO independent. Similar to our prior experiments on Summit, each comparision at a given node count utilizes a single job to ensure the allocated nodes are the same for all tested configurations. We evaluated each IOR configuration three times, with each run using five iterations on different files (i.e., with options '-m -i 5'), and report the IOR results from the best performing run for each configuration. For each configuration, IOR is executed once to write the shared file, and a second time to read back the previously written file.

Figure 5 shows the mean write and read bandwidth for GekkoFS and UnifyFS for shared files using POSIX I/O and MPI-IO. These tests use eight IOR client processes per node to match the expected application mapping on Crusher and Frontier (i.e., one MPI process per GCD), a transfer size of 8 MiB, and a single 512 MiB segment per process. UnifyFS uses its default RAS mode, no client or server extent caching, and its storage chunk size is set to match the IOR transfer size. Four cores (8 hardware threads) of each Crusher node are dedicated to the server for UnifyFS and GekkoFS.

As shown in Figure 5a, the write performance provided by both file systems is consistent between POSIX and MPI-IO. Due to its exclusive use of local data storage, UnifyFS provides nearly linear write bandwidth scaling of approximately 3.3 GiB/s per node (roughly 80% of the 4 GB/s available) up to 64

![](_page_8_Figure_7.png)

Fig. 5: IOR Shared File Write and Read Bandwidth using GekkoFS and UnifyFS (Crusher, 8 ppn)

nodes. Above 64 nodes, performance starts degrading due to the synchronization overhead that increases with the number of file extents. GekkoFS write bandwidth starts around 650 MiB/s per node and decreases significantly as more processes contribute to the shared file, presumably due to the need to transfer file data to an increasing number of remote servers. At 128 nodes, the GekkoFS write bandwidth is only about 31.5 GiB/s, or 250 MiB/s per node.

Figure 5b presents the read performance where once again UnifyFS benefits from its use of local data storage, while GekkoFS must use remote data access. At 128 nodes, UnifyFS provides roughly 50% greater bandwidth (i.e., 75 GiB/s vs. 50 GiB/s for GekkoFS). However, the benefit is much less than that for writes, since without extent caching all UnifyFS extent lookups are forwarded to the owner server.

# V. RELATED WORK

Burst buffers, tiered storage, and node-local storage have been prevalent in HPC systems for a while now and numerous projects have investigated methods for efficiently utilizing such hardware. The virtual parallel log-structured file system (PLFS) [13] was a foundational work that tried to fix the performance mismatch between an application's I/O burst with a slower parallel file system using a log-structured layout. PLFS provided better write performance than directly accessing a parallel file system, but the log structure limited read performance.

IndexFS provides a scalable metadata service to handle bursty metadata operations on top of existing parallel file systems, using a metadata management approach based on columnar log-structured files [14]. It focuses on improving metadata operation latency and throughput by load balancing directories across metadata servers, partitioning directories with large numbers of entries, and client caching and server indexing of recently accessed or updated metadata. The simple hash-based file owner metadata distribution technique used by UnifyFS also provides load balancing of metadata operations across servers for workloads with many files, such as fileper-process checkpointing, although we have yet to study the metadata performance of such workloads. BatchFS [15] extends IndexFS to provide the concept of private and auxiliary metadata servers, where private servers exist within a client application and auxiliary servers are processes co-located with clients on compute resources. In BatchFS' batch execution mode, metadata update operations are immediately made visible within the private server, then batched and forwarded to the local auxiliary server for consistency checking before publishing the changes to the global namespace maintained by the parallel file system. This approach is similar in nature to the relaxed consistency used in UnifyFS for extent metadata synchronization of shared file writes. However, namespace updates in UnifyFS are synchronizing operations that are immediately made visible to the global namespace. For the shared file workloads on which we focus, namespace update operations are far less frequent and have not been a performance bottleneck.

DAOS [16] is a scalable asynchronous object storage system designed for distributed non-volatile memory such as Intel Optane or NVMe that provides useful data storage abstractions including array or key-value storage objects, storage pools, and ephemeral data containers. DAOS is being deployed as a burst buffer tier within the ALCF Aurora system's storage hierarchy [17]. Similar to UnifyFS, DAOS has integrations to support POSIX I/O, HDF5, and MPI-IO. Currently, DAOS requires separate storage servers with persistent memory, and thus cannot be used to leverage NLS on HPC compute nodes.

With regard to efforts to provide a solution similar to UnifyFS (i.e., using fast NLS as a burst buffer for a larger parallel file system), projects tend to fall under two broad categories: 1) user-space libraries that intercept an application's I/O calls and redirect that I/O elsewhere (e.g., BurstFS [18], CHFS [19], GekkoFS [12], and Spectral [1]; and 2) complete parallel file systems that are designed to be ephemeral (e.g., Gfarm/BB [20], BeeOND [21]).

As a user-space I/O interception library designed to provide easy access to NLS for HPC applications, BurstFS [18] is the most directly related work, and UnifyFS benefited from the lessons learned in the development of BurstFS. BurstFS could not intercept I/O calls in dynamically linked libraries and thus required static linking of applications. The BurstFS consistency model was also much more limited than UnifyFS; all processes had to agree that writes to a file were complete before any reads were allowed. Finally, BurstFS used an MPIbased key-value store to manage file metadata. The dependency on MPI caused deployment complexity when using the file system with MPI-based applications.

GekkoFS [12] and Spectral [1] are user-space I/O interception libraries providing ephemeral namespaces on NLS. Both provide "relaxed" POSIX consistency to improve HPC I/O performance, and use server processes on each node to manage file operations. Unlike UnifyFS, Spectral does not provide internode communication and does not support reading remote data. GekkoFS does support remote data access, due to its wide-striping scheme to balance data distribution that eliminates the need for clients to consult a centralized metadata directory to determine which server handles a particular data chunk. However, wide-striping also means there is no way to optimize data placement for future accesses.

MadFS [22] is a custom implementation of the GekkoFS data and metadata management architecture for HPC systems based on the Arm CPU architecture that currently holds the first-place spot on the IO500 list [23]. In our comparison with GekkoFS we observed reduced per-node write bandwidth with increasing numbers of nodes. The IO500 results for MadFS also show such a downward trend, which we believe is caused by the wide-striping of data.

CHFS [19] is an ephemeral file system targeting nodelocal persistent memory devices such as Intel Optane, but alternatively supports NLS devices that provide a POSIX file system. In contrast, UnifyFS has the capability to use both memory-based and file-based storage concurrently. Unlike UnifyFS and GekkoFS, CHFS does not provide transparent I/O interception for HPC applications and instead requires either code modifications to directly use the CHFS client API that has POSIX-like file operations, or use of a FUSE-based implementation. CHFS is based on a distributed key-value storage architecture that uses ring-based consistent hashing to place and locate file data chunks across servers, similar to the data distribution method used by GekkoFS. CHFS exhibits fairly good scalability for I/O bandwidth and metadata operations rate in limited experiments up to 64 nodes.

Gfarm/BB [20] is an ephemeral burst buffer parallel file system, based on the Gfarm distributed file system [24]. Gfarm/BB keeps metadata information solely in RAM to boost I/O performance but may lose data if the node running the metadata server crashes. Lastly, BeeOND (BeeGFS-On-Demand) is an ephemeral parallel file system that uses compute nodes as storage servers. As a kernel-level file system, no additional mechanisms are necessary to intercept application I/O. However, BeeOND is fully POSIX-compliant which may limit HPC I/O performance.

# VI. CONCLUSION AND FUTURE WORK

In this paper, we described the goals and design of UnifyFS, a user-level file system that aggregates NLS tiers available on HPC systems and makes them available to applications under a unified namespace. UnifyFS employs transparent I/O interception, so it does not require changes to application code and is compatible with commonly used HPC I/O libraries. UnifyFS supports the common I/O behaviors of HPC applications and enables users to tune its semantics to provide faster performance when possible. We evaluated the performance of UnifyFS and demonstrated its excellent scaling performance for write operations that can improve the performance of checkpoint operations by as much as 53×.

For future work, we plan to improve on several elements of UnifyFS. First and foremost, we plan to investigate approaches that may enhance the performance and scalability of read operations to better support read-intensive workloads such as machine learning. Currently, application reads of locally written data are performed by the local server and data is provided to the client via shared memory, except when clientlocal metadata caching is enabled. We are currently evaluating an enhancement that allows any local client to directly read all local data. This still requires an RPC to the server to identify local data, but the actual read operations are made directly by clients. For remote data reads and writes, performance may benefit from improvements to our server threading model to allow better request concurrency.

The cost of moving checkpoint data to non-ephemeral storage is not included in our experiments. Many real applications checkpoint periodically (e.g., every hour) and only need the most recent checkpoint on stable storage to restart in a subsequent job. The design of UnifyFS supports two methods for persisting data, either by using an additional concurrently running client that moves checkpoints as a background task asynchronous to the application, or by staging-out the last completed checkpoint at the end of a job. We plan to study the performance of both approaches and their impacts to application execution.

Finally, using a more diverse set of production HPC applications may reveal the need to add support for currently unsupported I/O methods, such as file locking and comprehensive directory operations. We are particularly interested in supporting data analytics applications that utilize Python.

# ACKNOWLEDGMENTS

This research was supported by the Exascale Computing Project (17-SC-20-SC), a collaborative effort of the U.S. Department of Energy Office of Science and the National Nuclear Security Administration. This research used resources of the Oak Ridge Leadership Computing Facility, which is a DOE Office of Science User Facility supported under Contract DE-AC05-00OR22725. This work was performed under the auspices of the U.S. Department of Energy by Oak Ridge National Laboratory under Contract DE-AC05-00OR22725 and Lawrence Livermore National Laboratory under Contract DE-AC52-07NA27344. LLNL-CONF-829824.

#### REFERENCES

- [1] S. Oral, S. S. Vazhkudai, F. Wang, C. Zimmer, C. Brumgard, J. Hanley, G. Markomanolis, R. Miller, D. Leverman, S. Atchley, and V. V. Larrea, "End-to-end i/o portfolio for the summit supercomputing ecosystem,"
in SC '19: Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis. New York, NY, USA: Association for Computing Machinery, 2019.

- [2] Livermore's El Capitan Supercomputer to Debut HPE 'Rabbit' Near Node Local Storage, 2021. [Online]. Available: https://www.hpcwire.com/2021/02/18/ livermores-el-capitan-supercomputer-hpe-rabbit-storage-nodes/
- [3] A. Moody, G. Bronevetsky, K. Mohror, and B. R. d. Supinski, "Design, Modeling, and Evaluation of a Scalable Multi-level Checkpointing System," in Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis, 2010.
- [4] I. of Electrical and E. E. (IEEE), "IEEE Standard for Information Technology–Portable Operating System Interface (POSIX(TM)) Base Specifications, Issue 7," pp. 1–3951, 2018.
- [5] C. Wang, K. Mohror, and M. Snir, "File System Semantics Requirements of HPC Applications," in Proceedings of the 30th International Symposium on High-Performance Parallel and Distributed Computing, ser. HPDC '21, 2021.
- [6] UnifyFS: A file system for burst buffers, 2023. [Online]. Available: https://unifyfs.readthedocs.io/en/latest/
- [7] LLNL/UnifyFS: UnifyFS: A file system for burst buffers, 2023. [Online]. Available: https://github.com/LLNL/UnifyFS
- [8] mochi-hpc/mochi-margo: Argobots bindings for the Mercury RPC library, 2023. [Online]. Available: https://github.com/mochi-hpc/mochi-margo
- [9] S. Seo, A. Amer, P. Balaji, C. Bordage, G. Bosilca, A. Brooks, P. Carns, A. Castello, D. Genet, T. Herault ´ et al., "Argobots: A lightweight lowlevel threading and tasking framework," IEEE Transactions on Parallel and Distributed Systems, vol. 29, no. 3, pp. 512–526, 2017.
- [10] J. Soumagne, D. Kimpe, J. Zounmevo, M. Chaarawi, Q. Koziol, A. Afsahi, and R. Ross, "Mercury: Enabling remote procedure call for highperformance computing," in 2013 IEEE International Conference on Cluster Computing (CLUSTER), 2013, pp. 1–8.
- [11] LLNL/GOTCHA: GOTCHA is a library for wrapping function calls in shared libraries, 2023. [Online]. Available: https://github.com/LLNL/ GOTCHA
- [12] M.-A. Vef, N. Moti, T. Suß, T. Tocci, R. Nou, A. Miranda, T. Cortes, ¨ and A. Brinkmann, "Gekkofs-a temporary distributed file system for hpc applications," in 2018 IEEE International Conference on Cluster Computing (CLUSTER). IEEE, 2018, pp. 319–324.
- [13] J. Bent, G. Gibson, G. Grider, B. McClelland, P. Nowoczynski, J. Nunez, M. Polte, and M. Wingate, "Plfs: a checkpoint filesystem for parallel applications," in SC '09: Proceedings of the Conference on High Performance Computing, Networking, Storage and Analysis, 2009, pp. 1–12.
- [14] K. Ren, Q. Zheng, S. Patil, and G. Gibson, "IndexFS: Scaling file system metadata performance with stateless caching and bulk insertion," in SC '14: Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis, 2014, pp. 237–248.
- [15] Q. Zheng, K. Ren, and G. Gibson, "BatchFS: Scaling the file system control plane with client-funded metadata servers," in PDSW '14: Proceedings of the 9th Parallel Data Storage Workshop, 2014, pp. 1–6.
- [16] Z. Liang, J. Lombardi, M. Chaarawi, and M. Hennecke, DAOS: A Scale-Out High Performance Storage Stack for Storage Class Memory, 06 2020, pp. 40–54.
- [17] DAOS Tutorial, 2020. [Online]. Available: https: //www.alcf.anl.gov/sites/default/files/2020-03/2020-03%20slide% 20presentation%20DAOS.pdf
- [18] T. Wang, K. Mohror, A. Moody, K. Sato, and W. Yu, "An Ephemeral Burst-Buffer File System for Scientific Applications," in Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis, ser. SC '16, 2016, pp. 807–818.
- [19] O. Tatebe, K. Obata, K. Hiraga, and H. Ohtsuji, "CHFS: Parallel consistent hashing file system for node-local persistent memory," in HPC Asia2022. ACM, 2022, pp. 115–124.
- [20] O. Tatebe, S. Moriwake, and Y. Oyama, "Gfarm/bb—gfarm file system for node-local burst buffer," Journal of Computer Science and Technology, vol. 35, no. 1, pp. 61–71, 2020.
- [21] J. Heichler, "An introduction to beegfs," 2014.
- [22] K. Chen, "There is nothing mysterious behind madfs," 2021. [Online]. Available: https://www.youtube.com/watch?v=BJpkpA6hsDc& list=PLN0VUBsF9Di0Bsj4qia5SCqzBtTzGciA6&index=2
- [23] IO500 SC22 IO500 List, 2022. [Online]. Available: https://io500.org
- [24] O. Tatebe, K. Hiraga, and N. Soda, "Gfarm grid file system," New Generation Computing, vol. 28, no. 3, pp. 257–275, 2010.

