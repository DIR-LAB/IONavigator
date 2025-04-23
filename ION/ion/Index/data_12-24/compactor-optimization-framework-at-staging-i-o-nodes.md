# Compactor : Optimization Framework at Staging I/O nodes

Vishwanath Venkatesan1, Mohamad Chaarawi2, Quincey Koziol2 and Edgar Gabriel1

1Department of Computer Science, University of Houston 2The HDF Group {*venkates,gabriel*}*@cs.uh.edu*, {*chaarawi,koziol*}*@hdfgroup.org*

*Abstract*—Data-intensive applications are largely influenced by I/O performance on HPC systems and the scalability of such applications to exascale primarily depends on the scalability of the I/O performance on HPC systems in the future. To mitigate the I/O performance, recent HPC systems make use of staging nodes to delegate I/O requests and in-situ data analysis. In this paper, we present the *Compactor* framework and also present three optimizations to improve I/O performance at the data staging nodes. The first optimization performs collective buffering across requests from multiple processes. In the second optimization, we present a way to steal writes to service read request at the staging node. Finally, we also provide a way to "morph" write requests from the same process. All optimizations were implemented as a part of the Exascale FastForward I/O stack. We evaluated the optimizations over a PVFS2 file system using a micro-benchmark and Flash I/O benchmark. Our results indicate significant performance benefits with our framework. In the best case the compactor is able to provide up to 70% improvement in performance.

*Index Terms*—Parallel I/O, Staging I/O, Optimizations, Exascale FastForward I/O

## I. INTRODUCTION

HPC Applications require I/O systems that provide maximum I/O throughput and scale well with increasing number of cores and processors. A typical I/O stack of current HPC systems consists of several layers of middle-ware I/O libraries and parallel file systems such as: HDF5 [1], or Parallel NetCDF [2] on the top, an implementation of MPI I/O (e.g. ROMIO [3] or OMPIO [4]), and low level I/O interfaces such as POSIX I/O [5]. To satisfy the scalability challenges all layers in the stack have to be optimized and tuned.

Recent research suggests that having a staging area or an I/O forwarding layer can help mitigate the above discussed challenges imposed by scalability requirements [6], [7], [8]. This allows the application to use asynchronous methods and delegate I/O requests to nodes dedicated to perform I/O operations. Such a layer helps reduce the time spent by the application on I/O operations at the compute nodes. It also helps to overlap I/O with computation which in-turn reduces the total processing time of the application. In addition, having a staging I/O node can reduce system noise which can have adverse impact on the performance of applications [9], [10]. File system components are one of the main sources such system noises. In fact, parallel machines like Blue Gene/P use a stripped down version of the OS kernel without multiprocessing and POSIX I/O system calls on compute nodes to eliminate operating system noise [11]. The extraction of data from the compute nodes to the data staging nodes does indeed interfere with the communication performance between the compute nodes themselves. This issue can be addressed in several ways, one of which was done in [6].

However, the data staging layers, lack the benefit that could be obtained from the collective I/O style optimizations that client side parallel I/O APIs benefit from. This work focuses on filling this gap by developing a framework to provide such optimizations. In particular, the contributions of this paper are as follows:

- We describe a framework to efficiently implement I/O optimizations at staging nodes.
- We present three different optimizations namely, collective buffering, write stealing and write morphing to improve I/O performance from staging nodes.
- We demonstrate the implementation of this framework as a part of the Exascale FastForward I/O stack [12] and provide performance results on a parallel file system.

This paper is organized as follows: section II talks about some of the similar work in the literature. Section III introduces the Exascale FastForward I/O stack. Section IV presents the design of the compactor framework and section V discusses the three optimizations developed. Section VI presents the evaluation results and section VII provides the conclusion with some future work.

## II. RELATED WORK

In the recent years, there has been some effort invested in creating delegation based I/O architectures. The basic idea of these approaches is to reduce the overhead at the I/O servers by adding an additional layer in-between the compute nodes and the file-system's I/O servers called the forwarding layer to handle the stream of requests coming in from the various compute nodes.

DataStager [6] was one of the earliest efforts to provide support for staging I/O with ADIOS. The goal of this project was to provide complete asynchronous I/O support by ensuring the completion of transfer when the function call

![](_page_0_Picture_20.png)

returns. The work focused on increasing the I/O bandwidth by using RDMA operations to buffers in the staging nodes. Requests in the staging node are handled using different types of schedulers including a rate limiting scheduler, which also facilitates processing more than one request simultaneously. This work does not use any collective I/O style optimizations at the I/O forwarding layer as the requests received are already in POSIX I/O format.

ZOID [7] project had similar kind of architecture as that of datastager with scheduling policies to handle requests, but has support for MPI-I/O request at the staging nodes, in contrary to having just POSIX I/O requests. In addition, this project also provides support for merging requests from different compute nodes going to the same file at the staging node by matching file handles and grouping requests in a queue [13].

Another project which uses delegation based [8] architecture for I/O is built on top of the MPI I/O implementation ROMIO [3]. In this architecture a handful of nodes are selected from the compute nodes and made exclusively as staging nodes. I/O requests are intercepted by a plugin implemented in ROMIO and sent to IO delegate nodes. These nodes further optimize I/O requests into a smaller number of large and contiguous requests. To perform such optimizations the authors use a complete cache page management system [14] at the I/O delegate nodes. This is based on the client side caching work described in [15], [16]. The upper bound on the memory size was kept at 1GB, beyond which page eviction is done to cache other incoming requests.

As we can see all the approaches discussed above either provide either few or no optimizations at staging nodes. The work done with IOFSL [13] provide a basic form of request merging for I/O requests at staging nodes with request scheduler, but does not utilize the staging nodes to provide non-trivial optimizations such as write stealing (servicing read requests from writes). Although the cache based framework described in [14] could possibly provide the same set of optimizations as discussed in this paper, it would increase the memory consumption at the staging nodes in the process. In-addition the effectiveness of the optimizations would depend on the caching ability at the staging nodes. The approaches discussed in this paper provides ways to optimize the I/O requests without increasing memory pressure at staging I/O nodes, which can be critical with increasing workload of such nodes.

## III. EXASCALE FASTFORWARD I/O

The Exascale FastForward (EFF) [17] initiative is a program sponsored by the U.S. Department of Energy (DOE) for providing solutions to the next generation demands of computing. The Exascale FastForward I/O [12] project aims at providing an I/O stack for scalable and high performance I/O. The EFF I/O storage software stack contains several components essential to the proper functioning and performance of the application I/O.

![](_page_1_Figure_7.png)

Fig. 1: Exascale I/O Storage Software Stack (figure source [12])

Figure 1 shows the entire architecture and software stack proposed in the EFF I/O project. Applications will run on the compute nodes (CNs) and may use HDF5 [1] for their I/O. The HDF5 library will forward all data access operations to the I/O nodes (IONs) using Mercury [18], a fast Remote Procedure Call (RPC) mechanism with special support for large data transfer. The HDF5 library asynchronously ships all operations to the server and tracks dependencies between operations. This allows for a completely asynchronous behavior at the client side. The Mercury server(s), running on the IONs, will insert the operations received into the Asynchronous Execution Engine (AXE) with the required dependencies. When AXE schedules a task to execute, the HDF5 server module will translate each HDF5 call into I/O Dispatcher (IOD) call(s). I/O Dispatcher is built on top of PLFS [19] (Parallel Log File system), which stores data in a burst buffer (Non-Volatile RAM) and eventually migrates them to Distributed Application Object Storage (DAOS) [20] which is a next generation file system based on Lustre [21].

The work done in this paper is limited to the HDF5 server components running on the IONs, i.e. Mercury, Asynchronous Execution Engine, and HDF5 server module. The following sections will explain the role of the different components of the EFF I/O stack relevant to the work done in this paper.

## *A. HDF5 - VOL*

The Virtual Object Layer (VOL) [22] is an abstraction layer implemented just below the public HDF5 API, which intercepts HDF5 API calls that access objects in the file and forwards those calls to a plugin object driver. The plugins could actually store the objects in variety of ways. A plugin could, for example, have objects distributed remotely over different platforms, provide a raw mapping of the model to the file system, or even store the data in other file formats (like native netCDF or HDF4 format). The user still gets the same data model where access is done to a single HDF5 container; however the plugin object driver translates from what the user sees to how the data is actually stored. Figure 2 shows the general architecture of the HDF5 library with the VOL in place.

![](_page_2_Figure_1.png)

Fig. 2: General Architecture of HDF5 library with VOL [22]

An application running on the EFF I/O stack uses the IOD VOL plugin developed for the EFF project for storing its data. The IOD VOL plugin on the CNs (IOD VOL client) forwards the HDF5 VOL calls to the IONs using a function shipping library called Mercury. The IOD VOL client assigns a task ID to each HDF5 operation and tracks dependencies between those IDs. Each VOL call that is shipped to the IONs includes a list of task IDs that are required to complete before the operation can be executed. This allows for the completely asynchronous behavior at the application or client level.

The IOD VOL server component, running on the IONs, receives the VOL operations from the clients and inserts them into an asynchronous engine called AXE, that allows operations to be scheduled with dependencies between each other, as indicated by the IOD VOL client. Each task in the asynchronous execution engine maps an HDF5 VOL operation into one or more IOD API calls that are called once the task is scheduled to run.

## *B. Mercury: Function Shipper*

Mercury [18] is an Remote Procedure Call (RPC) mechanism that is used in the EFF stack to forward the HDF5 VOL calls made at the computer nodes to the I/O nodes. Mercury is generic to handle various types of operations and has a framework for extending support to other operations. Furthermore, different network abstractions can be used by mercury since those lower level network operations are abstracted in the Network Abstraction (NA) Layer. For this work, the MPI NA layer is used.

Calling functions in mercury with relatively small arguments results in using the short messaging mechanism exposed by the network abstraction layer, whereas functions containing large bulk data arguments, additionally uses RMA operations. The API for mercury is asynchronous supporting the EFF aim for an asynchronous API.

The Mercury servers running on the IONs receive the client requests and invokes the corresponding callbacks for each operation.

# *C. Asynchronous Execution Engine (AXE)*

The Asynchronous Execution Engine (AXE) supports asynchronous execution of tasks, which can have execution order dependencies. The AXE has several useful features:

- It provides a rich and intuitive interface for specifying functions and their dependency relationships
- An engine that asynchronously executes a function constrained to all its dependencies.
- Also provides a mechanism to monitor the status and results.
- Provides ways to define data structures to be passed around and shared across multiple function calls.

This is different from a typical non-blocking operation in the aspect that there is no need for progressing on any of the operations. The asynchronous engine maintains a thread pool from which it selects threads to progress tasks. AXE uses Directed Acyclic Graphs (DAG) to represent the dependencies and tasks, wherein the nodes of the DAG represent the tasks and the links between them represent a dependency. An example of an AXE task graph is shown in figure 3. The dependency in figure 3 should be read as follows:

- Task T2 cannot be scheduled without the completion of task T1.
- Tasks T4 and T5 can be scheduled simultaneously after the the completion of task T3.
- Task T11 can only be scheduled after either task T8 or T9 complete.
- BT13 (barrier-task) cannot be scheduled without the completion of tasks T1-T12 and so on.

![](_page_2_Figure_20.png)

Fig. 3: An example of an AXE task graph with a barrier task

## IV. COMPACTOR

Since this work looks at improving I/O performance at the I/O staging nodes, the focus is primarily at the I/O Forwarding Server of the EFF stack as shown in figure 1. As discussed in the previous sections, the primary purpose of this module is to insert the shipped VOL operations into an asynchronous engine (AXE) running on the ION, with possible dependencies on other VOL operations. These operations, when assigned a thread and scheduled by the AXE, translate the VOL operations into I/O Dispatcher (IOD)

![](_page_3_Figure_0.png)

Fig. 4: Original State of the I/O Forwarding Server

API calls. At this point, a feature called *"Compactor"* is developed to intercept I/O requests, before they are inserted into the AXE and look of opportunities to optimize the same. Figure 4 shows how I/O requests are handled originally by the I/O Forwarding Server, and figure 5 shows the modification to incorporate the compactor feature.

![](_page_3_Figure_3.png)

Fig. 5: Modified I/O Forwarding Server with the Compactor

Applying optimizations to I/O requests mandates the need for accumulating as many I/O requests as possible. To accomplish this, the raw I/O requests are delayed before the AXE schedules them. This will provide enough time to accumulate requests, possibly from multiple compute nodes, and determine if there could be any possibility for optimizations. Fortunately, high-performance use of the EFF storage stack already entails asynchronous execution of the raw data I/O tasks, and adding a small bit of additional delay to the execution of those tasks should have minimal effect on the application, while potentially having a large overall performance boost.

To create a delay in scheduling raw data I/O tasks, the following steps are followed. Whenever there is a raw data I/O request:

- The request is added to the compactor queue (this is where the optimizations are applied).
- The request manager checks to see if there is a compactor task currently in the AXE. If not, a compactor task (barrier-task) is created, with dependencies on all the currently executing tasks in the AXE.
- When the compactor task is executed by the AXE, the requests in the compactor queue are examined for optimizations (merging, short-circuiting, etc.) and the resulting set of raw data I/O operations are executed by the compactor task.
- Then compactor queue is then cleaned out, and the compactor task is rescheduled in the AXE, with dependencies on the raw data I/O operations just initiated

An important point to be noted is that the compactor currently focuses only on raw I/O requests. It does not handle metadata operations/synchronous I/O requests.

The compactor task can accumulate raw asynchronous I/O requests in the queue until the AXE schedules the compactor task. Alternatively, instead of depending on I/O tasks in the AXE, this compactor task could depend on a delay task (one that just sleeps for a certain amount of time), or a task that schedules only after a few AXE tasks are queued (the optimal time-stamp/number-of-requests can be left as a configurable parameter, passed in from the client side as a hint). Unfortunately, both of these approaches have downsides:

- Having a delay task in the AXE would waste an otherwise useful thread
- Changing the AXE to schedule tasks in a different way would entail large changes to its architecture.

In this work the compactor task is delayed depending on I/O tasks in the AXE.

## V. OPTIMIZATIONS ON STAGING NODES

This paper primarily focused on three different kinds of optimizations.

- Collective Buffering : Merging I/O requests from different compute nodes
- Write Stealing : Stealing read data from matching writes
- Write Morphing : Merging of overlapping I/O requests from one client

# *A. Collective Buffering*

This is the most fundamental form optimization used in collective I/O algorithms. In the case of the EFF stack, the I/O requests from multiple clients enter the server. In general, number of clients associated with each I/O server, can vary from hundreds to thousands. So there is a huge potential for merging requests from multiple clients. The main benefit of this optimization is to improve performance by reducing the contention to the underlying layers of the stack or the file system. Figure 6 shows an example for a typical collective buffering style optimization scenario.

![](_page_4_Figure_2.png)

Fig. 6: Example scenario for collective buffering

To perform the merging, the HDF5 selection(filetype) information is extracted from each individual I/O request. To merge the filetype the in-built HDF5 routines are used. The main challenge is to match the memory buffers to the merged file types. To accomplish this, we convert both file and memory types into a list of <offset, length> pairs which are inturn matched to provide the memory address for the merged filetype. Since HDF5 provides a higher level of abstraction and supports up to 32 dimensions, translation to list of <offset, length> pairs enables the compactor to also support multiple dimensions.

## *B. Write Stealing*

The compactor is capable of intercepting both read and write requests. This presents an unique opportunity for optimization. With read requests, its possible to compare it with the existing writes. In a scenario, where matching read and the write requests are in the same compactor queue, we can theoretically get the read data from the write buffers directly without touching the file system.

A read operation could be serviced from one or more write operations. An example of the this scenario has been shown in figure 7. To achieve this, the reads and writes are compared to check for overlaps. The parts of the filetype which overlap are copied directly from the write operations and the remainder is serviced from the file system. Logical operations between filetypes were facilitated by internal HDF5 routines. This optimization can be highly beneficial in case of visualization applications, where one process writes to a file and the other process reads to visualize the data. In such scenarios, if both the processes send their I/O requests to

![](_page_4_Figure_8.png)

Fig. 7: Scenario where we have read overlap with two writes

the same I/O staging node, write-stealing can be performed to ensure faster response to the visualization application. This can be hugely beneficial as it could provide rendering speeds similar to in-situ visualization approaches, with the data also being available for off-line visualization. Although this optimization can be very beneficial, there are couple of constraints with this optimization

- 1) Writes should happen before reads
- 2) In case where there is a need for fault-tolerance, reads have to get committed after writes. This can reduce the performance benefits.

## *C. Write Morphing*

Overlapping writes from multiple clients cannot be overlapped because of the lack of availability of temporal information in the current state of the stack. But in case of overlapping writes from the same client we will have both temporal and spatial information. In this case, writes can be allowed to overlap. This provides interesting prospects for optimizations. An example scenario where this can be useful is a multithreaded application trying to write to a file in an iterative loop, where subsequent writes overlap with the each other. In such a scenario, writes could be grouped as much as possible and the write buffers could be *morphed* together to form one write. This kind of optimization will greatly reduce the number of accesses to underlying file system/layers of the stack and in-addition, reduce the redundancy in writes.

![](_page_4_Figure_15.png)

Fig. 8: Example scenario for write morphing

Let us consider the scenario as shown in Figure 8. Here *Write I* happens first and *Write II* follows next. When these two write operations are merged, constructing a merged filetype could be created with a similar approach as used in collective buffering, but the challenge is in *morphing* the memory buffers with data from the *latest* writes. Let us assume that the two writes depicted in figure 8 roughly translates to these offsets shown in Table I. As you can see, when we try

| Write I | Write II | Merged |
| --- | --- | --- |
| 0 - 32 | 16 - 64 | 0 - 16 (I) |
| 48 - 96 | 80 - 96 | 16 - 64 (II) |
| 96 - 128 | 112 - 160 | 64 - 80 (I) |
| 160 - 256 | 176 - 208 | 80 - 96 (II) |
|  |  | 96 - 112 (I) |
|  |  | 112 - 160 (II) |
|  |  | 160 - 176 (I) |
|  |  | 176 - 208 (II) |
|  |  | 208 - 256 (I) |

TABLE I: Rough translation of figure 8 to offset ranges and expected merged offset ranges

to merge the offsets from the two writes, the memory buffer data needs to come from different writes for different offset ranges. Furthermore, to add to the complexity, there is also additional trouble with dynamically increasing size of the list of offsets. For example, if there is an overlap between offsetlength [0]: 0 → 64 and offset-length [7]: 16 → 32, then offset-length[0] will be broken into 0 → 16, 32 → 64. which increases the size of the list and offset-length[7] will now be pushed offset-length[8]. The algorithm designed for this purpose is able to accomplish this to create morphed memory buffers. In addition, like collective buffering write morphing is also done with <offset, length> pairs to support multiple dimensions.

## VI. EVALUATION

The efficiency of the optimizations discussed in section V were evaluated on the *crill* cluster at the University of Houston which consists of 16 nodes with four 12-core AMD Opteron (Magny Cours) processors each (48 cores per node, 768 cores total), 64 GB of main memory and two dual-port InfiniBand HCAs per node. The cluster has a PVFS2 (v2.8.2) parallel file system with 15 I/O servers and a stripe size of 1 MB. The file system is mounted onto the compute nodes over the second InfiniBand network interconnect of the cluster. The cluster utilizes slurm as a resource manager. MPICH2 (v3.0.2) was used with multi threading support

Since the EFF I/O stack is still under development and the lower layers of the stack have not been completely developed, native HDF5 I/O operations were used from the HDF5 server component to complete I/O requests. Although this approach has some limitations, it is sufficient to evaluate the effectiveness of the compactor. Moreover, modified usage of the stack means that relative performance improvements in measurements have more meaning than the actual performance values themselves. Measurements were performed using a micro benchmark developed to test the newly designed optimizations and an application benchmark called Flash I/O.

## *A. FFBench*

FastForward Benchmark (FFBench) suite consists of synthetically designed scenarios to evaluate the performance and efficiency of the compactor. The benchmark takes as input a configuration file to choose between different benchmarks and input sizes. One staging server in all our evaluations and an additional delay of 2μs was added to the compactor to accumulate requests. In the first test, the collective buffering

![](_page_5_Figure_9.png)

Fig. 9: FFBench test for collective buffering

![](_page_5_Figure_11.png)

Fig. 10: Total Write I/O requests (vs) Requests Merged

optimization of the compactor was evaluated. In this test, each process writes to different rows of a 2 dimensional matrix. The size of the matrix was kept at (np ∗ 512)×65536. Measurements were made with 16, 32, 64, 128 processes. The graph in figure 9 shows that the compactor is able to accumulate write requests, and we see that there is up to 30% performance improvement in comparison to the scenario without the compactor.

The performance improvement obtained comes from the requests that were merged. As shown in figure 10, irrespective of the total number of requests, the merged requests minimizes the number of writes between 16 − 32.

The second test focused on evaluating the write morphing optimization of the compactor by creating multiple overlapping writes to a file. The writes were created

![](_page_6_Figure_0.png)

Fig. 11: Write Morphing: Write to overlapping regions from one client

![](_page_6_Figure_2.png)

Fig. 12: Write Stealing: Reads to overlapping write regions from multiple clients

from one process as write morphing is not allowed across multiple clients. The size of the 2-D matrix was varied to see benefits. As shown in figure 11 we can see there is significant improvements obtained by using this approach. In the best case we see close to 40% performance improvement obtained with this optimization.

The write-stealing optimization was evaluated by extending the benchmark used for collective buffering with reads following the writes using similar selections (filetypes). The expectation is, if the reads and writes both land on the same compactor queue, then ideally we should see no time spent on reads. The figure 12 shows time spent in both the read and write operations. In majority of the cases the improvement obtained is close to 70%. This is because all the time spent in the read operations have been completely saved by the write stealing feature. This is more evident in the figure 13 which shows the percentage of time spent in the read/write operations. It is clear that with the compactor, all the time spent is only for the write operation and the read time is completely amortized.

![](_page_6_Figure_6.png)

Fig. 13: Write Stealing: Percentage of time spent in read/write for the test 12

## *B. Flash I/O*

The FLASH I/O benchmark suite [23] is an extracted I/O kernel from the FLASH [24] application. The FLASH application is a lock-structured adaptive mesh hydrodynamics code that solves fully compressible, reactive hydrodynamic equations, developed mainly for the study of nuclear flashes on neutron stars and white dwarfs [24] [14]. The benchmark produces a checkpoint file, a plotfile with centered data, and a plotfile with corner data. The plotfiles have single precision data.

![](_page_6_Figure_10.png)

Fig. 14: Flash I/O results for writing checkpoint files

The results of this benchmark has been shown in 14. We see that there is significant improvement in the performance obtained with the compactor. All these benefits are mostly from the collective-buffering approach as there are no scenarios where write-morphing or write-stealing can benefit. Despite that, we see that there is close to 42% reduction in the time consumed.

The amount of merging accomplished by the compactor can be seen in the chart 15. The results for generating plot files with corners has been shown in figure 16 and the results for generating plot files without corners has been shown in figure 17. Both these consume only a fraction of the time consumed by the check-pointing operation. But we can see almost 50-55% decrease in time consumption with

![](_page_7_Figure_0.png)

Fig. 15: Flash I/O: Merged vs Non-merged writes

![](_page_7_Figure_2.png)

Fig. 16: Flash I/O results for writing Plot files - with corners

optimizations from the compactor. Overall from the results we can conclude that having a feature like the compactor can prove to be very beneficial for I/O stacks.

# VII. CONCLUSION

This paper presents a framework to capture I/O requests and specify optimizations at staging I/O nodes. We also provide three different optimizations to compact requests at the staging node. The first optimization focuses on combining adjacent requests from multiple clients, in the second optimization we provide an approach to service read requests from matching write requests at the compactor and the final optimization allows to combine overlapping write requests from a single client by morphing their memory buffers. The framework and the optimizations have been implemented as an extension to the current Exascale FastForward I/O stack. Our results demonstrates significant improvements in the I/O time spent in comparison to scenarios without the compactor. Our evaluations showed 35% to 70% reduction in time spent in I/O operations for both the microbenchmark and the application scenario.

This work can be extended in multiple directions, including more application scenarios which can benefit from the *write*

![](_page_7_Figure_8.png)

Fig. 17: Flash I/O results for writing Plot files - without corners

*morphing* and *write stealing* optimizations. We can also make the compactor deterministic by using hints from the application, which can guarantee the merging of all requests that could be compacted. In addition, optimizations at staging nodes largely depend on the request being asynchronous, but even if the user uses synchronous I/O requests there are opportunities to optimize those, which could be a extension of this work. For synchronous raw data read I/O calls, the *write stealing* optimization could be applied by matching them with pending asynchronous writes. Synchronous raw data write I/O calls, could be merged with an already en-queued asynchronous write I/O operation. Although, aggregating synchronous operations with pending asynchronous operations must be carefully performed, because this aggregation could lead to degradation performance of the synchronous operation in cases of a small synchronous I/O request aggregated with a large asynchronous I/O request.

# ACKNOWLEDGMENTS

The work was done as a summer project funded by Intel. We would like to thank, Eric Barton, John Bent, Bryon Neitzel, Ruth Aydt and Jerome Sougmane from the Exascale FastForward I/O team for the assistance and support. We would also like acknowledge Neil Fortner for providing the Asynchronous Execution Engine(AXE) library. We would also like to thank, The HDF group for providing resources and support for successful completion of this work.

## REFERENCES

- [1] The HDF Group. (2000-2010) Hierarchical data format version 5. [Online]. Available: http://www.hdfgroup.org/HDF5
- [2] J. Li, W.-k. Liao, A. Choudhary, R. Ross, R. Thakur, W. Gropp, R. Latham, A. Siegel, B. Gallagher, and M. Zingale, "Parallel netcdf: A high-performance scientific i/o interface," in *Proceedings of the 2003 ACM/IEEE conference on Supercomputing*, ser. SC '03. New York, NY, USA: ACM, 2003, pp. 39–. [Online]. Available: http://doi.acm.org/10.1145/1048935.1050189
- [3] R. Thakur, W. Gropp, and E. Lusk, "On implementing MPI-IO portably and with high performance," in *Proceedings of the sixth workshop on I/O in parallel and distributed systems*, 1999, pp. 23–32.
- [4] M. Chaarawi, E. Gabriel, R. Keller, R. L. Graham, G. Bosilca, and J. J. Dongarra, "Ompio: a modular software architecture for mpi i/o," in *Proceedings of the 18th European MPI Users' Group conference on Recent advances in the message passing interface*, ser. EuroMPI'11. Berlin, Heidelberg: Springer-Verlag, 2011, pp. 81–89. [Online]. Available: http://dl.acm.org/citation.cfm?id=2042476.2042487

- [5] The Open Group Base Specifications Issue 7, "IEEE Std 1003. l-2008." [Online]. Available: http://www.opengroup.org/onlinepubs/9699919799/
- [6] H. Abbasi, M. Wolf, G. Eisenhauer, S. Klasky, K. Schwan, and F. Zheng, "Datastager: scalable data staging services for petascale applications," in *Procoeedings of the 18th ACM international symposium on High performance distributed computing*, ser. HPDC '09. New York, NY, USA: ACM, 2009, pp. 39–48. [Online]. Available: http://doi.acm.org/10.1145/1551609.1551618
- [7] K. Iskra, J. W. Romein, K. Yoshii, and P. Beckman, "Zoid: I/oforwarding infrastructure for petascale architectures," in *Proceedings of the 13th ACM SIGPLAN Symposium on Principles and practice of parallel programming*, ser. PPoPP '08. New York, NY, USA: ACM, 2008, pp. 153–162.
- [8] A. Nisar, W.-k. Liao, and A. Choudhary, "Delegation-based i/o mechanism for high performance computing systems," *IEEE Trans. Parallel Distrib. Syst.*, vol. 23, no. 2, pp. 271–279, Feb. 2012. [Online]. Available: http://dx.doi.org/10.1109/TPDS.2011.166
- [9] P. Beckman, K. Iskra, K. Yoshii, and S. Coghlan, "Operating system issues for petascale systems," *SIGOPS Oper. Syst. Rev.*, vol. 40, no. 2, pp. 29–33, Apr. 2006. [Online]. Available: http://doi.acm.org/10.1145/1131322.1131332
- [10] P. Beckman, K. Iskra, K. Yoshii, S. Coghlan, and A. Nataraj, "Benchmarking the effects of operating system interference on extreme-scale parallel machines," *Cluster Computing*, vol. 11, no. 1, pp. 3–16, Mar. 2008. [Online]. Available: http://dx.doi.org/10.1007/s10586- 007-0047-2
- [11] I. journal of Research and D. staff, "Overview of the ibm blue gene/p project," *IBM J. Res. Dev.*, vol. 52, no. 1/2, pp. 199–220, Jan. 2008. [Online]. Available: http://dl.acm.org/citation.cfm?id=1375990.1376008
- [12] Eric Barton, "Exascale fastforward i/o project," https://users.soe.ucsc.edu/ ivo//blog/2013/04/07/the-ff-stack/, 2012.
- [13] K. Ohta, D. Kimpe, J. Cope, K. Iskra, R. Ross, and Y. Ishikawa, "Optimization techniques at the i/o forwarding layer," in *Proceedings of the 2010 IEEE International Conference on Cluster Computing*, ser. CLUSTER '10. Washington, DC, USA: IEEE Computer Society, 2010, pp. 312–321.
- [14] A. Nisar, W.-k. Liao, and A. Choudhary, "Scaling parallel i/o performance through i/o delegate and caching system," in *Proceedings of the 2008 ACM/IEEE conference on Supercomputing*, ser. SC '08. Piscataway, NJ, USA: IEEE Press, 2008, pp. 9:1–9:12. [Online]. Available: http://dl.acm.org/citation.cfm?id=1413370.1413380
- [15] W. K. Liao, A. Ching, K. Coloma, A. Choudhary, and L. Ward, "An implementation and evaluation of client-side file caching for MPI-IO," in *Parallel and Distributed Processing Symposium, 2007. IPDPS 2007. IEEE International*, 2007, pp. 1–10.
- [16] W.-K. Liao, K. Coloma, A. Choudhary, and L. Ward, "Cooperative Client-Side File Caching for MPI Applications," *Int. J. High Perform. Comput. Appl.*, vol. 21, no. 2, pp. 144–154, 2007.
- [17] Department of Energy. Doe exascale technology acceleration. Https://sites.google.com/a/lbl.gov/exascale-initiative/.
- [18] *Mercury: Enabling Remote Procedure Call for High-Performance Computing*, Indianapolis, IN, 2013.
- [19] J. Bent, G. Gibson, G. Grider, B. McClelland, P. Nowoczynski, J. Nunez, M. Polte, and M. Wingate, "Plfs: a checkpoint filesystem for parallel applications," in *Proceedings of the Conference on High Performance Computing Networking, Storage and Analysis*, ser. SC '09. New York, NY, USA: ACM, 2009, pp. 21:1–21:12. [Online]. Available: http://doi.acm.org/10.1145/1654059.1654081
- [20] E. Barton, "Lustre FastForward to Exascale," http://www.opensfs.org/wp-content/uploads/2013/04/LUG-2013-Lustre-Fast-Forward-to-Exascale.pdf.
- [21] Johann Lombardi, "Lustre Restructuring," http://tinyurl.com/q7jayh4.
- [22] Mohamad Chaarawi. HDF5 Virtual Object Layer. http://tinyurl.com/qj3glq5.
- [23] M. Zingale, "Flash I/O Benchmark Routine parallel HDF5."
- [24] B. Fryxell, K. Olson, P. Ricker, and et. al, "Flash: An adaptive mesh hydrodynamics code for modeling astrophysical thermonuclear flashes," in *The Astrophysical Journal Supplement Series*, 2000, pp. 273–334.
- [25] H. Abbasi, J. Lofstead, F. Zheng, S. Klasky, K. Schwan, and M. Wolf, "Extending i/o through high performance data services," in *IN CLUSTER COMPUTING*. IEEE International, 2007.
- [26] N. Ali, P. H. Carns, K. Iskra, D. Kimpe, S. Lang, R. Latham, R. B. Ross, L. Ward, and P. Sadayappan, "Scalable i/o forwarding framework for high-performance computing systems." in *CLUSTER*. IEEE, 2009, pp. 1–10.

- [27] R. Riesen, R. Brightwell, P. G. Bridges, T. Hudson, A. B. Maccabe, P. M. Widener, and K. Ferreira, "Designing and implementing lightweight kernels for capability computing," *Concurr. Comput. : Pract. Exper.*, vol. 21, no. 6, pp. 793–817, Apr. 2009. [Online]. Available: http://dx.doi.org/10.1002/cpe.v21:6
- [28] S. M. Kelly and R. Brightwell, "Software architecture of the light weight kernel, catamount," in *In Cray User Group*, 2005, pp. 16–19.
- [29] J. Moreira, M. Brutman, J. Castanos, T. Engelsiepen, M. Giampapa, ˜ T. Gooding, R. Haskin, T. Inglett, D. Lieber, P. McCarthy, M. Mundy, J. Parker, and B. Wallenfelt, "Designing a highly-scalable operating system: the blue gene/l story," in *Proceedings of the 2006 ACM/IEEE conference on Supercomputing*, ser. SC '06. New York, NY, USA: ACM, 2006.
- [30] J. Sougmane, "An in-situ visualization approach for parallel coupling and steering of simulations through distributed shared memory files," Ph.D. dissertation, University of Bordeaux, France, 2012.
- [31] L. Yotong, "Hpc system at nudt," 2013. [Online]. Available: http://www.exascale.org/mediawiki/images/c/ca/Talk24-NUDT.pdf
- [32] "China's tianhae-2 caps top 10 supercomputer," 2013.
- [33] M. Chaarawi, "Optimizing performance of parallel i/o operations for high performance computing," Ph.D. dissertation, The University of Houston, 2011.
- [34] OpenFabrics Alliance, "OpenFabrics webpage http://www.openib.org," Last accessed on April, 2011.
- [35] Myricom, "Myrinet webpage http://www.myri.com/myrinet/overview/," Last accessed on May, 2009.
- [36] Quadrics, "Quadrics webpage http://www.quadrics.com/," Last accessed on May, 2009.
- [37] J. Lofstead, F. Zheng, S. Klasky, and K. Schwan, "Adaptable, metadata rich io methods for portable high performance io," in *In Proceedings of IPDPS'09, May 25-29, Rome, Italy*, 2009.
- [38] Dolphin, "Dolphin webpage http://www.dolphinics.com/," Last accessed on May, 2009.
- [39] R. Thakur, E. Lusk, and W. Gropp, "I/O in parallel applications: The weakest link," *The International Journal of High Performance Computing Applications*, vol. 12, no. 4, pp. 389–395, Winter 1998.
- [40] R. Thakur and W. Gropp, "Improving the Performance of Collective Operations in MPICH," in *Recent Advances in Parallel Virtual Machine and Message Passing Interface*, ser. LNCS, J. Dongarra, D. Laforenza, and S. Orlando, Eds., no. 2840. Springer Verlag, 2003, pp. 257–267, 10th European PVM/MPI User's Group Meeting, Venice, Italy.
- [41] J. F. Lofstead, S. Klasky, K. Schwan, N. Podhorszki, and C. Jin, "Flexible io and integration for scientific codes through the adaptable io system (adios)," in *Proceedings of the 6th international workshop on Challenges of large applications in distributed environments*, ser. CLADE '08. New York, NY, USA: ACM, 2008, pp. 15–24. [Online]. Available: http://doi.acm.org/10.1145/1383529.1383533
- [42] R. K. Rew and G. P. Davis, "The unidata netcdf: Software for scientific data access," in *Sixth International Conference on Interactive Information and Processing Systems for Meteorology, Oceanography, and Hydrology*, 1990, pp. 33–40.
- [43] Lustre webpage, *http://www.lustre.org*, Last accessed on April, 2011.
- [44] Hierarchical Data Format Group, *Parallel HDF5*, http://www.hdfgroup.org/HDF5/PHDF5/.
- [45] H. Yu, R. Sahoo, C. Howson, G. Almasi, J. Castanos, M. Gupta, J. Moreira, J. Parker, T. Engelsiepen, R. Ross, R. Thakur, R. Latham, and W. Gropp, "High performance file i/o for the blue gene/l supercomputer," in *High-Performance Computer Architecture, 2006. The Twelfth International Symposium on*, 2006, pp. 187–196.
- [46] PVFS2 webpage, *Parallel Virtual File System*, http://www.pvfs.org, Last accessed on April, 2011.
- [47] W. Gropp, E. Lusk, N. Doss, and A. Skjellum, "A high-performance, portable implementation of the MPI message passing interface standard," *Parallel Computing*, vol. 22, no. 6, pp. 789–828, Sep. 1996.

