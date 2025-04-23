# I/O-Aware Flushing for HPC Caching Filesystem

Osamu Tatebe *University of Tsukuba* Tsukuba, Ibaraki, Japan tatebe@cs.tsukuba.ac.jp

Kohei Hiraga *University of Tsukuba* Tsukuba, Ibaraki, Japan hiraga@ccs.tsukuba.ac.jp

Hiroki Ohtsuji *Fujitsu Limited* Kawasaki, Kanagawa, Japan ohtsuji.hiroki@fujitsu.com

*Abstract*—The increasing difference in performance between computing and storage has caused significant problems for HPC systems. To reduce the difference in performance, intermediate storage layers have been introduced; however, the flushing strategy is a significant issue in these layers. Dirty data must be flushed to efficiently utilize the intermediate storage layers although this may degrade I/O performance and cause instability because data access and flushing interfere with each other. In this study, an I/O-aware mechanism that does not interfere with I/O activity is proposed for data flushing, using HPC-specific workloads. Evaluations based on HPC application benchmarks in MPI-IO and NetCDF demonstrated the performance advantages of the proposed I/O-aware flushing, with the I/O performance of the intermediate storage layers displaying minimum degradation and remaining stable during flushing.

*Index Terms*—caching file system, I/O-aware flushing, intermediate storage layers, burst buffer, parallel file system

#### I. INTRODUCTION

The increasing difference in performance between computing and storage is becoming a significant problem in high-performance computing (HPC) systems. To reduce this performance difference, intermediate storage layers with much better performance but smaller capacity than those of parallel file systems (PFSs) have been introduced between compute nodes and PFSs. Examples of this implementation include shared burst buffers and compute-node local storage [5].

Efficient transparent use of intermediate storage layers remains a challenge because of several issues. One of the most significant issues is how and when to flush data from the intermediate storage layers to the backend PFS. When flushing data, the interference causes instability and degradation in the storage performance of the intermediate storage layers.

To address this issue, an I/O-aware flushing method is proposed in this study. This flushing strategy exploits HPCspecific workloads that involve iterative computing and I/O phases with almost no I/O activity occurring during the computing phase. When I/O-aware flushing detects a phase change, it flushes the data during the computing phase to avoid interference from intermediate storage layers.

In addition, an MPI-IO interface was implemented for the proposed intermediate storage layer, while there is no direct relationship between MPI-IO and IO-aware flushing. Because MPI-IO is a standard parallel I/O interface in HPC, most applications can utilize this I/O-aware flushing strategy without any source code modification.

The contributions of this study are as follows:

- An I/O-aware flushing approach is proposed to flush data when there is no I/O activity, to avoid I/O performance degradation.
- An MPI-IO interface was implemented for the intermediate storage layer because most HPC applications utilize I/O-aware flushing without code modification.
- The advantages of I/O-aware flushing are demonstrated through evaluations on MPI-IO and NetCDF HPC applications.

The remainder of this paper is organized as follows: In Section II, studies that flush data from intermediate storage layers to the backend PFS are described. In Section III, the design of I/O-aware flushing is introduced. Section IV provides the details of the proposed implementation. In Section V, the advantages of I/O-aware flushing are discussed with respect to HPC applications. Finally, Section VI presents the conclusions of this study.

#### II. RELATED STUDIES

Numerous systems have been proposed for intermediate storage layers to improve the storage performance of backend PFSs. Several ad hoc PFSs utilize intermediate storage layers [20], [26], [27], [15], [24], [19]. These systems, which are separate from the backend PFS, construct a temporal PFS using compute-node local storage during the execution of a job [4], whereby users and batch-queuing systems employ stage-in and stage-out files from and to the backend PFS, respectively. However, these operations are complicated and prone to error.

These issues can be solved by adding caching functionality to the intermediate storage layers, whereby data movement from and to the backend PFS can be processed automatically or by using certain tools. Dirty cache entries in the intermediate storage layers are managed for the write-back cache functionality. SymphonyFS [16], which is a write buffer for the backend PFS, uses compute-node local storage to store logs and supports a single-shared-file write pattern. The BeeGFS-based caching file system [1] extends BeeGFS [25] by adding caching functionality using compute-node local storage. Files are stripped and stored in node-local storage among compute nodes. One study utilized a GPFS to manage an NVRAM-based storage cache [6]. This system exploits the information lifecycle management of GPFS to move data between the cache and backend PFS. All of these systems flush data using a watermark-based strategy, which flushes data

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:52:30 UTC from IEEE Xplore. Restrictions apply.

<sup>11</sup>

when the caching data reach the watermark. Watermark-based flushing is disadvantageous because it significantly degrades I/O performance when flushing starts. This I/O deterioration is worse when the capacity of the intermediate storage layers increases, thereby increasing the amount of flush data. A solution to this issue is to set the watermark larger than the size required by the HPC application; however, this may not be suitable when the capacity required by the application is greater than the physical capacity of the intermediate storage layers.

An input rate-based approach [7] was proposed to overcome the disadvantages of watermark-based approaches, which are unsuitable for numerous storage arrays and network-attached storage servers used for high-speed incoming write applications. To avoid obstructing the incoming I/O data, the input rate-based approach flushes the data based on the input rate to mitigate the large flushing overhead caused by the watermarkbased approach. The method proposed in this study is similar to this approach in that data are flushed without being stored until the watermark is reached. Periods with no I/O activity are then utilized to flush the data without interference.

CHFS/Cache [21] is a caching file system based on CHFS [20]. It extends CHFS to add caching and flushing functionality to the backend PFS under reasonably relaxed consistency semantics to avoid exacerbating metadata performance. The CHFS/Cache introduces background flush threads to flush data asynchronously, which requires the specification of various flush timings, the detailed descriptions of which and evaluations were not provided in the study. To address this issue, we propose a new I/O-aware flushing strategy, and evaluate it using CHFS/Cache.

The HDF5 Cache VOL (Virtual Object Layer) [30] is an external HDF5 connector used to cache data from the HDF5 library, whereby background threads are introduced to flush data asynchronously. The data are flushed immediately and the file-closing operation waits for the flush operation. However, this strategy may interfere with the writing and flushing of data.

UniviStor [28] is a log-based write-back caching system that uses hierarchical storage, including storage on compute nodes. The logs are flushed asynchronously to the PFS during the file-closing operation, which may interfere with access to the next file.

Hermes [11] is a multi-tiered distributed I/O buffering system. The trigger to flush the buffered data is configurable and can be set to immediate, at file closing, at job termination, or periodical. However, all configurations cannot avoid interference of data access and flushing.

Tang et al. proposed a draining strategy to regulate bursty I/O behavior [18]. This exploits the I/O periodicity and scatters the I/O draining process within the I/O interval. This approach mitigates interference of data access and flushing, but does not eliminate it because it flushes data regardless of the I/O activity.

The burst-buffer-based I/O orchestration framework TRIO [29] orchestrates the order in which dirty chunks are

![](_page_1_Figure_8.png)

Fig. 1. Caching parallel file system implemented between compute nodes and backend PFS; data caching is transparent to users.

flushed to improve sequentiality, which mitigates contention among the storage servers of the backend PFS. This technique is orthogonal to the proposed method, which pertains to the timing of flushing data, whereas TRIO is concerned with the order of dirty chunks to be flushed. Both TRIO and the proposed method can be used simultaneously.

Several studies have been conducted on shared burst buffer interference [23], [12], [13]. However, the interference discussed in these studies differs from that investigated in our study. These studies considered the interference from other applications because the burst buffer is shared among users. However, we consider the interference arising from flushing and accessing data. This implies that these proposals are orthogonal to ours such that in the case of node-local storage, there is no interference from other applications; however, in the case of a shared burst buffer, both types of interference must be considered. These proposals can also be used simultaneously.

To the best of our knowledge, a flushing strategy that avoids performance interference while accessing and flushing data has not yet been reported. Hence, an I/O-aware flushing strategy is proposed to avoid performance interference by exploiting the periods with no I/O activity in HPC-specific workloads.

#### III. DESIGN OF CACHING PARALLEL FILE SYSTEM

The caching PFS is used to conceal the complexity of hierarchical storage systems. It is implemented between compute nodes and the backend PFS, and its function is to make data caching transparent to users, as shown in Fig. 1. In this study, a caching PFS was constructed using compute-node local storage during job execution. The compute-node local storage can be occupied by a user application without any need to consider interference with other user applications.

The file data and metadata in the backend PFS are staged into the caching PFS via either a batch queuing system or ondemand data access. When creating or updating the caching PFS, this file is created or updated. The created or updated file chunk is referred to as a dirty chunk and flushed to the backend PFS. This section presents a method for achieving efficient data flushing.

# *A. Design of I/O-aware flushing*

Efficient data flushing is difficult to achieve. Data flushing can interfere with the reading and writing of the cached data. Therefore, data should be flushed when the caching PFS does not perform any I/O activities.

In this study, a new flushing strategy, known as I/O-aware flushing, is proposed to address I/O activities. The design goals of I/O-aware flushing are as follows:

- Flushing is not performed during the I/O phase to avoid interference with I/O activities of the caching PFS.
- Flushing is executed during the computing phase when there is no I/O activity.

HPC applications, including machine learning applications, involve alternating iterations of computing and I/O phases. During the computing phase, most computations and communications are performed with almost no I/O activity. In contrast, bursty I/O occurs in the I/O phase. HPC applications typically generate snapshots or checkpoint data after each iteration. In machine learning, numerous small files are read randomly during this phase. With I/O-aware flushing, data are flushed only during the computing phase without any I/O activity and not during the I/O phase.

The most challenging issue in I/O-aware flushing is the detection of phase changes without modification of application code. The computing and I/O phases can be determined most accurately by modifying the application code; however, this procedure may be challenging to users. In addition, code modification is not an option when the source code is not available.

During I/O-aware flushing, the I/O activities are monitored on each file server of the caching PFS. Lack of I/O activity on the file server indicates that a change in the computing phase can be considered. However, I/O activity may disappear within a short period during the I/O phase. Hence, a phase change is indicated when no I/O activity occurs for a specified period of time.

The period with no I/O activity, hereafter referred to as *wait interval*, is a parameter in I/O-aware flushing. If the wait interval is too short, a phase change may be detected more frequently than expected. The IOR benchmark [14] typically creates, reads, and deletes a single shared file. In this case, all three operations are I/O phases. If the wait interval is too short, data flushing may begin between file creation and reading or between file reading and deletion. This may interfere with I/O activities, but the interference would be minimal because I/Oaware flushing stops flushing data when I/O activities resume. If the wait interval is sufficiently long, no data are flushed because all the data are deleted in the caching PFS. If the wait interval is too long, the time period may be too short for flushing all the dirty data during the computing phase. In this case, a watermark-based approach can be helpful because of the increase in dirty data in the caching PFS. This design does not require system-wide global management, which often hinders scalability. In I/O-aware flushing, each file server of the caching PFS detects a phase change and flushes the data independently.

Thus, I/O-aware flushing is beneficial for temporal files. Temporal files are created and accessed during the execution of applications, but are not necessarily flushed. When temporal files are generated, read, and deleted during the I/O phase, I/O-aware flushing does not flush these temporal files, whereas with immediate and close-time flushing unnecessary temporal files are flushed.

# IV. IMPLEMENTATION OF CACHING PARALLEL FILE SYSTEM

This section describes the implementation of the I/O-aware flushing strategy and MPI-IO interface of the caching PFS based on the open-source CHFS/Cache.

#### *A. Implementation of I/O-aware flushing*

CHFS/Cache features a thread-safe flush queue for flushing data. Updated file chunks are referred to as dirty chunks. Dirty chunk information is sent to the flush queue. A specified number of active flush threads dequeue the dirty chunk information, thereby flushing the dirty chunk in parallel.

For I/O-aware flushing, the I/O activities in the file servers of the caching PFS must be monitored to determine the specified wait interval during which there is no I/O activity. Hence, we introduced an activity counter to monitor the I/O remote procedure calls (RPCs). The activity counter is incremented and decremented at the beginning and end of I/Orelated RPCs, respectively, indicating the number of ongoing I/O activities. The I/O activities on the file server can be monitored using this activity counter.

Flushing begins after a specified wait interval with no I/O activity. Two condition variables, no activity and io activity, were introduced to ensure waiting for the specified interval with no I/O activity. The no activity condition variable is signaled when the activity counter is zero, and the io activity condition variable is signaled when the activity counter is incremented. If the activity counter is greater than zero, wait until the no activity condition variable is signaled. Then, wait for the wait interval using the io activity condition variable. If no signal is delivered in the wait interval, the flush is triggered.

#### *B. Implementation of MPI-IO*

MPI-IO for CHFS/Cache was implemented based on MPICH version 4.0.2 [2]. MPICH uses ROMIO [22] as its MPI-IO library. We introduced a new type of ROMIO ADIO for CHFS/Cache which can also be used for other MPI implementations such as MVAPICH, Intel MPI and Open MPI.

ADIO includes 27 basic I/O operations; however, it is not necessary to implement all the functions because generic functions are provided. For example, if a collective strided read function is not implemented, a generic collective strided read function is used, which calls contiguous read functions for the CHFS/Cache. To fill the semantic gap between MPI-IO and CHFS/Cache and provide better performance, ADIO functions were implemented as follows:

*1) Open:* This function creates or opens a file. In native CHFS APIs, file creation and opening are performed using different APIs. If the create flag is set, then chfs_create is called; otherwise, chfs_open is called.

In the case of collective creation, with multiple processes creating a single file, the following steps are performed in ROMIO: A process of rank zero creates a file and closes it; subsequently, the file is opened in all processes without any specific attention accorded to the ADIO layer.

*2) Resize:* This function resizes files. In MPI, this is a collective function and is called by multiple processes. The same file does not need to be resized in all processes because resizing via a single process is sufficient. In the ADIO for the CHFS/Cache, barrier synchronization is performed, whereby a process of rank zero resizes the file, and the result is broadcast to avoid redundant resize operations.

*3) Read and write:* The read function reads the data from a file, whereas the write function writes the data to a file. The data size and file offset are provided by the arguments of the function. MPI-IO provides three types of file pointers: explicit, individual, and shared. With the explicit file pointer, the file offset can be used as provided and translation is not required. For an individual file pointer, the file offset must be modified by the individual file pointer. Currently, shared file pointers are not implemented, because they are rarely used and exhibit poor I/O performance.

*4) Initialization and termination:* There is no initialization or termination interface for the I/O library in ADIO; however, a native CHFS/Cache API requires them. For initialization, a hook is introduced into MPI Init() for the I/O initialization call. For an environment in which the MPI library cannot be modified, a backup plan is introduced to call the I/O initialization at the first call of ADIO functions, such as open and delete. This solution is portable, because it is purely an ADIO implementation.

The I/O termination function can be specified from a delete callback function of MPI Comm create keyval(). This is the standard method for calling I/O termination function.

*5) Data sieving:* Data sieving is an optimization technique used to improve small random I/O performance and is not a function of ADIO. This requires a byte-range locking function to perform read-modify-write. Because CHFS/Cache does not support byte-range locking, this optimization was disabled.

# V. EVALUATION

This section presents the evaluation results of the proposed I/O-aware flushing method, hereafter referred to as *CACHE-A*. CACHE-A was compared to the immediate flushing strategy, denoted as *CACHE-I*. These two flushing strategies were then compared with the raw CHFS that does not feature caching functionality, denoted as *CHFS*, and the Lustre parallel file system, denoted as *Lustre*. Raw CHFS is considered an ideal case in which all flushing overheads are hidden because data are not flushed. We do not evaluate the watermarkbased approach, but the flushing overhead is expected to be much higher than that of CACHE-I after the watermark is

![](_page_3_Figure_9.png)

Fig. 2. Storage configuration for performance evaluation. In Lustre, nodelocal storage is not used. In CHFS, data are stored on an ad hoc PFS without flushing. In CACHE-I and CACHE-A, data are written to an ad hoc PFS and flushed to the backend PFS. Flushing is performed immediately in CACHE-I and by I/O-aware flushing in CACHE-A.

reached. CACHE-A, CACHE-I, and CHFS use compute-node local storage, whereas Lustre does not. Fig. 2 shows the configurations of Lustre, CHFS, CACHE-I, and CACHE-A. For CACHE-A and CACHE-I, the remaining unflushed dirty data are flushed at job termination.

A Pegasus supercomputer at the University of Tsukuba was used for the evaluation. Pegasus is a 120-node cluster with each node comprising a 2.1 GHz 48-core Xeon CPU (codenamed Sapphire Rapids), 128 GiB DDR5 memory, and 2 TiB Intel Optane persistent memory 300 series. Each compute node was connected using InfiniBand NDR200.

The backend PFS was Lustre 2.12 [3], which comprises 11 1.92 TB NVMe SSDs (eight data, two parity, and one hot-spare drives) for metadata targets (MDTs) and 534 18 TB 7.2K rpm nearline SAS HDDs (16 declustered RAID pools, each having 33 drives with eight data and two parity block redundancies, and six hot-spare drives) for object storage targets (OSTs). Two active-active metadata servers (MDSs) were provided by one DataDirect Networks ES200NV, and each was connected by two lanes of the InfiniBand EDR100. Four object storage servers (OSSs) were provided by two DataDirect Networks ES7990Xs comprising two active-active controllers, each connected by four lanes of InfiniBand EDR100.

# *A. RDBench*

RDBench [9] is a numerical simulation application for reaction-diffusion systems [17] based on the Gray-Scott model [8]. This calculates the time evolution of two chemicals as they diffuse and react with each other. The two global twodimensional arrays are divided into chunks and held by each MPI process. In the computing phase, MPI processes perform two-dimensional five-point stencil calculations and exchange halos with neighboring processes. Following each computing phase, a global two-dimensional array is written to a file using MPI-IO. The MPI-IO interface allows RDBench to be executed on CHFS/Cache without any code modification. Each two-dimensional array chunk is tiled into a subarray of the global two-dimensional array using MPI_File_set_view.

![](_page_4_Figure_0.png)

Fig. 3. RDBench execution time breakdown on up to 64 compute nodes with 25 processes per node.

![](_page_4_Figure_2.png)

Fig. 4. Average I/O bandwidth of RDBench with up to 64 nodes and 25 processes per node. Error bars indicate 95% confidence intervals.

Each process performs a strided write, and the overall I/O pattern is two-dimensional block-cyclic.

For this evaluation, we measured the weak-scaling performance using up to 64 compute nodes on a Pegasus supercomputer with 25 processes per node. One CHFS server process was executed at each compute node. The CHFS server processes receive file write requests from the MPI application processes and flush the data to the backend Lustre. Eight threads were used to flush the data. This benchmark generates a single shared file in the I/O phase. As each process generated 512 MiB of data, the output file size was 800 GiB for 64 nodes, with 25 processes per node. This benchmark has ten iterations, generating ten output files. Because the transfer size for each write is 64 KiB, both the chunk size for CHFS and the stripe size for Lustre were set to 64 KiB. When writing files directly from the application to Lustre, Lustre's stripe count was set to the same number as the number of MPI processes using the over-stripe function for better performance. The performance is unacceptable without over-striping. When using Lustre as a backend for the CHFS/Cache, the stripe count was set to the number of CHFS servers, which is equal to the number of client nodes.

Fig. 3 is a stacked bar graph breaking down benchmark execution time into Init, Comm, Comp, IO, and Finalize corresponding to the times required for initialization, halo communication, stencil computation, MPI parallel I/O, and finalization, respectively. In the case of CACHE-A and CACHE-I, Finalize includes the time required to flush the remaining dirty data on the persistent memory to Lustre. We performed ten measurements and obtained the average. The x-axis represents the number of compute nodes and increases from 1 to 64.

With weak scaling evaluations, ideally, the execution time remains the same as the number of nodes increases. For initialization and stencil computation, there was no significant difference among the cases. In the case of CHFS, the time required for communication and I/O increased moderately as the number of nodes increased. The I/O time was only 2.9 times longer with 64 nodes than with one node. The communication time of CACHE-A increased slightly because of the conflict of network resources between communication and flushing, but the I/O time was almost the same as that of CHFS because CACHE-A can avoid interference of CHFS access and flushing. Because not all data can be flushed during the computing phase, finalization requires time to flush the remaining dirty data; however, CACHE-A was better than CACHE-I in terms of total execution time. The I/O time of CACHE-I was longer than that of CACHE-A because of interference. The I/O time of Lustre increased as the number of nodes increased because the I/O performance does not scale. The I/O time with 64 nodes was 11.9 times longer than that with one node.

Fig. 4 shows the average I/O bandwidth of RDBench. The average and error bars are shown for each configuration; the error bars represent 95% confidence intervals. Concurrent single-shared-file write performance for a total of 64 nodes was 12.2 GiB/s for Lustre and 89.6 GiB/s for CACHE-A with a 1-second wait interval. CACHE-A achieved 7.33 times better bandwidth than Lustre. Compared to CHFS, which has no caching function, the bandwidth of CACHE-I was 28% lower, whereas CACHE-A showed almost the same bandwidth. I/Oaware flushing successfully avoided I/O degradation during immediate flushing.

### *B. LESBench*

LESBench, which is a proxy application benchmark of City-LES [10], simulates the flow field in idealized buildings located uniformly in a region. This benchmark primarily involves advection-diffusion simulation, solves the Poisson equation, and computes the sub-grid scale model. LESBench

![](_page_5_Figure_0.png)

Fig. 5. LESBench execution time breakdown on Pegasus up to 64 compute nodes with 32 processes per node.

1 2 4 8 16 32 64 0 10 20 30 40 50 60 Bandwidth [GiB/s] CHFS (no flush, no persistency) CACHE-A CACHE-I Lustre 

Fig. 6. Average I/O bandwidth of LESBench on Pegasus with 32 processes per node, for nodes 1–64. Error bars show 95% confidence interval.

Number of nodes

is written in Fortran 90 using NetCDF on top of a parallel HDF5. Because the MPI-IO interface was implemented for CHFS/Cache, LESBench can be executed on CHFS/Cache without any code modification. LESBench is an application that iterates the computing and I/O phases, similar to RD-Bench. In this evaluation, 50 computation steps were performed, and snapshot data were generated every 10 steps in NetCDF format.

For this evaluation, we measured the performance of weak scaling using up to 64 compute nodes on a Pegasus supercomputer with 32 processes per node. Each MPI process writes multi-dimensional arrays, often 3-dimensional or 4 dimensional arrays generated by the simulations, resulting in approximately 1.46 GiB of output data per process, excluding metadata, which is equivalent to 2.93 TiB of output data for 64 nodes.

Unlike RDBench, LESBench writes data in NetCDF format, so the chunk sizes of Lustre and CHFS cannot match the alignment of the writes. The stripe size for Lustre was set to 1 MiB, and the chunk size for CHFS was set to 512 KiB. Lustre's stripe count was set to the same as RDBench's, except for the 64-node Lustre case where we set over-stripe to the upper limit of 2,000, even though the process count was 2,048.

Fig. 5 shows the execution time breakdown of the benchmark for nodes 1–64. We performed ten measurements and obtained the average values. For weak scaling evaluations, ideally, the execution time remains the same as the number of nodes increases. The computation times did not differ significantly among the cases. The I/O time of the CHFS increased moderately as the number of nodes increased. The I/O time of CHFS-A was similar to that of CHFS; however, the finalization time increased slightly because not all data can be flushed in the computing phase.

Fig. 6 shows the average I/O bandwidths. Error bars represent 95% confidence intervals. The I/O bandwidth was measured five times. The average and error bars are shown for each configuration; the error bars represent 95% confidence intervals. Lustre had an average bandwidth of 14.1 GiB/s with 32 nodes. CHFS and CACHE-A were scaled up to 32 nodes with an average bandwidth of 62.3 GiB/s for 32 nodes, which is 4.43 times better than that of Lustre. CACHE-I was also scaled up to 32 nodes with an average bandwidth of 49.9 GiB/s for 32 nodes, which is 19.9% lower than that of CACHE-A.

With 64 nodes, the bandwidth of CHFS was not improved. We have not figured out the reason, but CACHE-A performed better than CACHE-I.

# VI. CONCLUSION

In this study, I/O-aware flushing was designed to avoid I/O degradation of intermediate storage layers caused by the interference generated when flushing and accessing data simultaneously. With I/O-aware flushing, data are flushed when there is no I/O activity, assuming that HPC-specific workloads consist of iterative computing and I/O phases. The design of I/O-aware flushing is universal, and thus applicable to other application domains. We implemented I/O-aware flushing in CHFS/Cache. In addition, an MPI-IO interface for the CHFS/Cache was implemented to support most HPC applications without code modification.

Performance evaluation revealed the advantages of I/Oaware flushing. RDBench demonstrated that CHFS/Cache was more advantageous than Lustre because of its single-sharedfile write pattern. In the case of 64 nodes, the I/O bandwidth of CACHE-A was 7.33 times that of Lustre. Immediate flushing displayed 28% lower bandwidth, whereas I/O-aware flushing displayed no degradation in I/O performance. LESBench also demonstrated that CHFS/Cache was more advantageous than Lustre because it benefited from the single-shared-file write pattern. In the case of 32 nodes, the I/O performance of CACHE-A was 4.43 times that of Lustre. The bandwidth of CACHE-I was 19.9% lower than that of CACHE-A because of interference. I/O-aware flushing successfully avoids I/O degradation during immediate flushing. The source code used in this study was released in https://github.com/otatebe/chfs as version 3.0.0, and https://github.com/range3/mpich/tree/chfs.

# ACKNOWLEDGMENT

This work was partially supported by JSPS KAKENHI Grant Number JP22H00509, JP22K17897, "Research and Development Project of the Enhanced Infrastructures for Post-5G Information and Communication Systems" (JPNP20017), commissioned by the New Energy and Industrial Technology Development Organization (NEDO), MEXT as "Feasibility studies for the next-generation computing infrastructure", the Multidisciplinary Cooperative Research Program in CCS, University of Tsukuba, and Fujitsu Limited.

# REFERENCES

- [1] D. Abramson, C. Jin, J. Luong, and J. Carroll, "A BeeGFS-based caching file system for data-intensive parallel computing," in *Supercomputing Frontiers. SCFA 2020*, ser. Lecture Notes in Computer Science, vol. 12082, 2020, pp. 3–22.
- [2] Argonne National Laboratory, *MPICH High-Performance Portable* MPI, 1992. [Online]. Available: https://www.mpich.org/
- [3] P. Braam, "The Lustre storage architecture," 2019.
- [4] A. Brinkmann, K. Mohror, W. Yu, P. Carns, T. Cortes, S. A. Klasky, A. Miranda, F.-J. Pfreundt, R. B. Ross, and M.-A. Vef, "Ad hoc file systems for high-performance computing," *Journal of Computer Science and Technology*, vol. 35, no. 1, pp. 4–26, 2020.
- [5] L. Cao, B. W. Settlemyer, and J. Bent, "To share or not to share: Comparing burst buffer architectures," in *Proceedings of the 25th High Performance Computing Symposium*, ser. HPC '17, 2017.
- [6] S. El Sayed, S. Graf, M. Hennecke, D. Pleiter, G. Schwarz, H. Schick, and M. Stephan, "Using GPFS to manage NVRAM-based storage cache," in *Supercomputing*, J. M. Kunkel, T. Ludwig, and H. W. Meuer, Eds., 2013, pp. 435–446.
- [7] S. Faibish, P. Bixby, J. Forecast, P. Armangau, and S. Pawar, "A new approach to file system cache writeback of application data," in *Proceedings of the 3rd Annual Haifa Experimental Systems Conference*, ser. SYSTOR '10, 2010.
- [8] P. Gray and S. K. Scott, "Autocatalytic reactions in the isothermal, continuous stirred tank reactor: Isolas and other forms of multistability," *Chemical Engineering Science*, vol. 38, no. 1, pp. 29–43, Jan. 1983.
- [9] K. Hiraga, "rdbench: 2D reaction-diffusion system benchmark using MPI and MPI-IO." Jul. 2022. [Online]. Available: https://github.com/range3/rdbench
- [10] R. Ikeda, H. Kusaka, S. Iizuka, and T. Boku, "Development of urban meteorological LES model for thermal environment at city scale," in *Poster presented at 9th International Conference on Urban Climate*, 2015, pp. 1–5.
- [11] A. Kougkas, H. Devarajan, and X.-H. Sun, "I/O acceleration via multitiered data buffering and prefetching," *Journal of Computer Science and Technology*, vol. 35, pp. 92–120, 2020.
- [12] A. Kougkas, H. Devarajan, X.-H. Sun, and J. Lofstead, "Harmonia: An interference-aware dynamic I/O scheduler for shared non-volatile burst buffers," in *2018 IEEE International Conference on Cluster Computing (CLUSTER)*, 2018, pp. 290–301.
- [13] W. Liang, Y. Chen, and H. An, "Interference-aware I/O scheduling for data-intensive applications on hierarchical HPC storage systems," in *2019 IEEE 21st International Conference on High Performance Computing and Communications (HPCC)*, 2019, pp. 654–661.
- [14] W. Loewe, T. McLarty, and C. Morrone, *HPC IO Benchmark Repository*, 2018. [Online]. Available: https://github.com/hpc/ior/
- [15] A. Moody, D. Sikich, N. Bass, M. J. Brim, C. Stanavige, H. Sim, J. Moore, T. Hutter, S. Boehm, K. Mohror, D. Ivanov, T. Wang, and C. P. Steffen, "UnifyFS: A distributed burst buffer file system - 0.1.0," 10 2017.

- [16] S. Oral, S. S. Vazhkudai, F. Wang, C. Zimmer, C. Brumgard, J. Hanley, G. Markomanolis, R. Miller, D. Leverman, S. Atchley, and V. V. Larrea, "End-to-end I/O portfolio for the Summit supercomputing ecosystem," in *Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*, ser. SC '19, 2019.
- [17] J. E. Pearson, "Complex Patterns in a Simple System," *Science*, vol. 261, no. 5118, pp. 189–192, Jul. 1993.
- [18] K. Tang, P. Huang, X. He, T. Lu, S. S. Vazhkudai, and D. Tiwari, "Toward managing HPC burst buffers effectively: Draining strategy to regulate bursty I/O behavior," in *2017 IEEE 25th International Symposium on Modeling, Analysis, and Simulation of Computer and Telecommunication Systems (MASCOTS)*, 2017, pp. 87–98.
- [19] O. Tatebe, S. Moriwake, and Y. Oyama, "Gfarm/BB != Gfarm file system for node-local burst buffer," *Journal of Computer Science and Technology*, vol. 35, no. 1, pp. 61–71, 2020.
- [20] O. Tatebe, K. Obata, K. Hiraga, and H. Ohtsuji, "CHFS: Parallel consistent hashing file system for node-local persistent memory," in *International Conference on High Performance Computing in Asia-Pacific Region*, ser. HPCAsia2022, 2022, pp. 115–124.
- [21] O. Tatebe and H. Ohtsuji, "Caching support for CHFS node-local persistent memory file system," in *2022 IEEE International Parallel and Distributed Processing Symposium Workshops (IPDPSW)*, 2022, pp. 1103–1110.
- [22] R. Thakur, W. Gropp, and E. Lusk, "Data sieving and collective I/O in ROMIO," in *Proceedings. Frontiers '99. Seventh Symposium on the Frontiers of Massively Parallel Computation*, 1999, pp. 182–189.
- [23] S. Thapaliya, P. Bangalore, J. Lofstead, K. Mohror, and A. Moody, "Managing I/O interference in a shared burst buffer system," in *2016 45th International Conference on Parallel Processing (ICPP)*, 2016, pp. 416–425.
- [24] ThinkParQ, *BeeOND: BeeGFS On Demand*, 2018. [Online]. Available: https://www.beegfs.io/wiki/BeeOND
- [25] ThinkParQ and Fraunhofer, *BeeGFS*, 2018. [Online]. Available: https://www.beegfs.io/
- [26] M.-A. Vef, N. Moti, T. Suß, M. Tacke, T. Tocci, R. Nou, A. Miranda, ¨ T. Cortes, and A. Brinkmann, "GekkoFS != a temporary burst buffer file system for HPC applications," *Journal of Computer Science and Technology*, vol. 35, no. 1, pp. 72–91, 2020.
- [27] T. Wang, K. Mohror, A. Moody, K. Sato, and W. Yu, "An ephemeral burst-buffer file system for scientific applications," in *SC '16: Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis*, 2016, pp. 807–818.
- [28] T. Wang, S. Byna, B. Dong, and H. Tang, "UniviStor: Integrated hierarchical and distributed storage for HPC," in *2018 IEEE International Conference on Cluster Computing (CLUSTER)*, 2018, pp. 134–144.
- [29] T. Wang, S. Oral, M. Pritchard, B. Wang, and W. Yu, "TRIO: Burst buffer based I/O orchestration," in *2015 IEEE International Conference on Cluster Computing*, 2015, pp. 194–203.
- [30] H. Zheng, V. Vishwanath, Q. Koziol, H. Tang, J. Ravi, J. Mainzer, and S. Byna, "HDF5 Cache VOL: Efficient and scalable parallel I/O through caching data on node-local storage," in *2022 22nd IEEE International Symposium on Cluster, Cloud and Internet Computing (CCGrid)*, 2022, pp. 61–70.

