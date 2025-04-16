# I/O Performance Evaluation on Multicore Clusters with Atmospheric Model Environment

Carla Osthoff 1 , Claudio Schepke2 , Jairo P anetta3 , P ablo Grunmann1 , N icolas M aillard2 , P hilippe N avaux2 , P edro L. Silva Dias1 , P edro P ais Lopes3

1 Laboratorio Nacional de Computac¸ ´ ao Cient ˜ ´ıfica (LNCC) Caixa Postal 25651 – 075 – Petropolis – RJ – Brazil ´ osthoff,pldsdias,pablojg@lncc.br,

2 Instituto de Informatica – Universidade Federal do Rio Grande do Sul (UFRGS) ´ Caixa Postal 15.064 – 91.501-970 – Porto Alegre – RS – Brazil cschepke,nicolas,navaux@inf.ufrgs.br,

3 Instituto Nacional de Pesquisas Espaciais (INPE) Caixa Postal 12630-000 – Cachoeira Paulista – SP – Brazil jairo.panetta,pedro.lopes@cptec.inpe.br

WWW home page: http://gppd.inf.ufrgs.br/atmosferamassiva

# Abstract

*This work evaluates the I/O performance in a multicore cluster environment for an atmosphere model for weather and climate simulations. It contains large data sets for I/O in scientific applications. The analysis demonstrates that the scalability of the system gets worse as we increase the number of cores per machine, with greater impact on output operations. We also demonstrate poor capacity of the multicore system for providing high aggregate I/O bandwidth and that the scalability is not improved when I/O operations are running trough a parallel file system neither running on local disk.* 1

# 1. Introduction

Multi-core processors are prevalent nowadays in systems ranging from embedded devices to large-scale high performance computing systems. Over the next decade the degree of on-chip parallelism will significantly increase and processors will contain tens and even hundreds of cores. This will increase the impact of multiple levels of parallelism on clusters. Running multiple processes of the same application or even different applications on the same node is usual. Each application tends to issue contiguous I/O requests individually, but if multiple processes issue many I/O requests simultaneously, the requests are handled by the local file system in a non-contiguous way. This is because each process tends to issue contiguous requests, however, they can be interrupted by the requests of other nodes. Then, the number of disk seeks increases, and the I/O effective bandwidth falls.

Moreover, recent workload studies show that many HPC storage systems are used to store many small files in addition to the large ones. Further investigation finds that these files come from a number of sources, not just one misbehaving application [2]. Several scientific domains such as climatology, astronomy, and biology generate data sets that are most conveniently stored and organized in a file system as independent files.

In this scenario, it is imperative to investigate the scale of programs for such workload applications on multilevel parallelism environments. Therefore, this work evaluates the I/O performance in a multicore environment for a large data sets I/O scientifc application, as complementary work for memory and cache contention multicore research investigations.

In order to validate our work we run our experiments with the atmosphere model simulation application, " Ocean Land Atmospheric Model " (OLAM), which is a typical

<sup>1</sup>Supported by CNPq.

large data sets I/O scientific application organized as independent files.

The contribution of this work is to show that the scalability of large data sets I/O scientific applications organized as independent files gets worse as we increase the number of cores per machine, with greater impact on the output operations. Also our work shows that, on a multicore environment, the scalability is not improved when I/O operations are running trough a parallel file system neither running on local disks. Therefore in order to scale in a high performance computing system, for those scientific applications, the multicore I/O bottleneck needs to be resolved.

The remainder of this paper is organized as follows. In the next section we present related work. Section 3 presents the atmosphere model performance problem and the OLAM algorithm. The performance evaluation, experimental results and experimental analysis are presented in section 4. The last section presents conclusions and future works.

# 2 Related Works

#### 2.1 Multicore Memory Contention

Data access latency has been a problem even on singlecore systems, as processors are much faster than memory. With the emergence of multicore processors, a more severe problem arises with data access due to the limited bandwidth to access shared resources in the memory hierarchy. When multiple cores are processing different sets of data, the shared resource becomes a performance bottleneck if the bandwidth is not high enough to support the multiple cores. This has been already experienced in currently available processors [13]. In order to better use multicore resources, the work of [12] introduces simple analytical models for predicting the occurrence of data access contention and provides a guideline for choosing optimal number of cores to avoid data access contention while ruling an application.

Another work [3] presents a set of effective optimizations and an auto-tuning environment that searches over the optimizations and their parameters to minimize runtime. The strategy allows performance portability over multiple architectures, due to auto-tuning.

#### 2.2 Parallel File Systems on Multicore Environment

As shown in a recent work [9], the I/O challenge for current parallel file system is to support highly concurrent metadata accesses generated by multiple cores. The work of [9] presents a technique that attempts to bridge the increasing performance and scalability gap between the compute and I/O components by shipping I/O calls from compute nodes to dedicated I/O nodes. The I/O nodes perform operations on behalf of the compute nodes and can reduce file system traffic by aggregating, rescheduling, and caching I/O requests.

Processes on a parallel application tend to issue contiguous I/O requests individually, but if multiple processes issue I/O requests simultaneously the requests are handled by the local file system in a non-contiguous way. This performance degradation is more critical in parallel file systems. To solve this problem, the work of [10] proposes an Gather-Arrange-Scatter (GAS) node-level I/O request reordering architecture for parallel file systems. The main idea is that I/O requests issued from the same node are gathered and buffered locally, then buffered requests are arranged in a better order which reduces the I/O cost at I/O nodes, and finally scattered to I/O nodes in parallel.

OLAM file access pattern is a multiple-file parallel approach applied to a message-passing application, therefore every task accesses its own file. Scalability problems arises when trying to create/write files simultaneously in the same directory, since these requests may be serialized due to metadata server contention. Writing the files into separate directories is not a viable alternative, as it only shifts the problem to creating the directories. The work of [4] shows that current parallel file system is not a viable alternative. The reason is that while offering optimizations for a variety of file access patterns, the particular strength of current parallel file systems is to provide efficient concurrent access to a single file via file striping across multiple disks and replicated I/O servers. The work of [4] presents a parallel I/O library that reduces file creation overhead and simplifies file handling without penalizing read and write performance.

Parallel file systems used in High Performance Computing are increasingly specialized to extract the highest possible performance for large I/O operations, at the expense of other potential workloads. While some applications have adapted to I/O best practices and can obtain good performance on these systems, many applications such as OLAM use many small files. In order to improve I/O performance in multicore environments accessing a large number of small files, the work of [2] describes five techniques for optimizing small file access in parallel file systems for very large scale systems.

#### 3 Atmosphere Model Performance Problem

High speed implementation of atmospheric models is fundamental to operational activities on weather forecast and climate prediction, due to execution time constraints — there is a pre-defined, short time window to run the model. Model execution cannot begin before input data arrives, and cannot end after the due time established by user contracts. Experience in international weather forecast centers points to a two-hour window to predict the behavior of the atmosphere in the next few coming days. The computational complexity of atmospheric and environmental models is O(n 4 ), where n is the number of latitude (or longitude) grid points to cover the horizontal geographical domain of the model also, the number of vertical points is expected to increase with n and necessarily the number of time-steps required to cover the same amount of time also increase proportionally to n. The spacing between consecutive points, or conversely, the number of points used to cover an amount of space (called "resolution") strongly influences the accuracy of results. Operational models worldwide use the highest possible resolution that would allow the model to run at the stabilized time window in the available computer system. New computer systems are selected for their ability to run the model at even higher resolutions during the available time window. Given these limitations, the impact of multiple levels of parallelism and multicore architectures in the execution time of operational models is indispensable research.

Numerical models have been used extensively in the last decades to understand and predict the climate and weather phenomena. In general, there are two kinds of models, differing on their domain: global (entire Earth) and regional (country, state, etc). Global models have spatial resolution of about 0.2 to 1.5 degrees of latitude and therefore cannot represent very well the scale of regional weather phenomena. The central limitation is computing power. Regional models, on the other hand, have higher resolution but are restricted to limited area domains. Forecasting the future on a limited domain demands the knowledge of future atmospheric conditions at domain borders. Therefore, limited area models require previous execution of global models.

In order to provide both global and regional simulations, a novel, interesting approach was recently developed at Duke University. The main feature of this model called Ocean-Land Atmosphere Model (OLAM) is to provide a global grid that can be locally refined, forming a single grid. That allows simultaneous representation (and forecasting) of both the global scale and the local scale phenomena, as well as bi-directional interactions among scales [15].

OLAM was developed in FORTRAN 90 and recently parallelized with Message Passing Interface (MPI) under the Single Program Multiple Data (SPMD) model.

#### 3.1 OLAM Typical simulation Analysis

An OLAM typical simulation requires reading about 0.5Gb of input files and initial conditions. Typical input files are: Global Initial Conditions at a certain date and time and global maps describing Topography, Soil type, Ice covered areas, Olson Global Ecosystem (OGE) vegetation dataset, Depth of the soil interacting with the root zone, Sea surface temperature and Normalized Difference Vegetation Index (NDVI). OLAM application typically writes a 2 Mb output history file, 200 Kb output plot files for each core and 500 Kb output results files for each core. Therefore, as we increase the number of cores, we increase the number of independent output files. We divide the OLAM algorithm in three parts; the parameter initialization part, the atmosphere time state calculation part and the output write results part. Finally, we inserted timestamps barriers on selected points of OLAM source (a few module boundaries) in order to evaluate the partial execution times for OLAM routines.

# 4 Performance Evaluation

#### 4.1 Simulation Environment

![](_page_2_Figure_9.png)

**Figure 1. Cluster Multicore OLAM Speed-up**

The performance measurements were made on two multicore clusters platforms: a SUN machine and an SGI ICE machine. The SUN platform at the National Laboratory of Scientific Computing (LNCC) is composed of 23 dual node Intel Xeon E5440 Quad-Cores with 4 MB of cache and 16 GB of RAM memory in each node, interconnected by an *Infiniband* network. The ICE platform at the Institute of Informatics of the Federal University of Rio Grande do Sul is composed of 14 dual node Intel Xeon E5310 Quad-Cores of 1.6 Ghz with 4 Mb of cache and 16 Gb of RAM memory in each node, interconnected by a Gygabit Ethernet network. In addition, MPICH version 2-1.2.p1 implementation has been used for all the tests.

![](_page_3_Figure_0.png)

![](_page_3_Figure_1.png)

**Figure 2. OLAM timestamps barriers processing time percentage for 128 cores**

We evaluate the scalability of the code in SUN platform multicore machine with the timestamp barriers disabled. Figure 1 presents the 128 core speed-up on that machine. Results show that the scalability of the system halts at 32 cores, which is very poor. In order to find the algorithm routines that impact the execution time the most, we enabled nine timestamp barriers at selected portions of the code.

Synchronization time represents the time overlap between the first and the last process that reach the barrier. Consequently, lower barrier synchronization times signalize even load balancing, while higher barrier synchronization times signalize load imbalance.

As we increase the number of processors, we observe that I/O execution time increases. For instance, Figure 2 presents the execution time for each timestamp barrier for 128 core run. Observe that the timestamps that dominate the execution time are number 6, 9 and 9 sync, which are related to output operations, therefore we call 6plot, 9write and 9wrtsync respectively. Timestamp number 6plot represents graphics initialization time and number 6plotsync represents related synchronization time. Timestamp number 9write represents output execution time and number 9wrtsync represents related synchronization time.

Timestamp number 8 represents execution time for timestep calculation, therefore we call 8exec and timestamp number 1 is related to input file read operations, therefore we call 1read. The remaining timestamps execution times are negligible, therefore are not represented in Figure 2.

In order to better illustrate the timestamps execution time from Figure 2, we observe that OLAM timestep calculation, which is timestamp number 8exec from Figure 2, takes only 4.12 seconds from total execution time, which is 115.18 seconds long. This results shows that for a 128 cores run, the execution of I/O operations takes over 95% of total execution time, explaining the poor scalability.

#### 4.2.1 Local disk I/O operations performance evaluation

Trying to decrease I/O operation execution time, we redirected I/O operations to SUN local disks. As expected, the execution time of I/O operations decreased, but scalability remains modest.

![](_page_3_Figure_11.png)

**Figure 3. OLAM cores running in the same machine speed-up compared to cores running 1 core per machine speed-up and Linear speed-up.**

The suspicion of node I/O contention due to multicore dictated a new set of experiments. Figure 3 presents measured results: the speed-up from 1 to 8 cores executing I/O operations on local disks varying the assignment of processes to cores. Figure 3 dark bar denotes 8 cores running on the same machine environment, gray bar denotes 8 cores running 1 core per machine environment and dashed bar represents linear speed-up. Experiments were run with timestamp barriers disabled. Observe that OLAM performance gets worse with the increase of cores per node, showing I/O contention even on local disks.

In order to evaluate routines that increase execution time as we increase the number of cores, we ran OLAM with selected 9 timestamp barriers from the last section. We observe that even for a small number of cores timestamps numbers 6out, 9out and 9outsync, which are related to output operations, dominate performance overhead.

We observe timestamps increasing time for all timestamps barriers from 8 cores running in the same machine for 8 cores running 1 per machine. Also, core 0 timestamp 1read increases execution time from 8 cores running 1 core per machine for 8 cores running in the same machine. This is related to multicore overhead for read operation of input initialization files. On multicore environment, problem arises with data access latency due to the limited bandwidth to access shared resources in the memory hierarchy [13] [12].

Timestamp 6plot increasing time is related to multicore initialization files overhead. OLAM plotting files access pattern have a multiple-file parallel approach applied to a message-passing application, therefore every core accesses its own file. In the multicore environment scalability problems get worse when trying to create/writing files simultaneously in the same directory, since these requests may be serialized due to metadata server contention [4].

Timestamp 9write increasing time is related to multicore output file overhead. In the multicore environment all cores are accessing a large number of small files issuing I/O requests simultaneously therefore requests are handled by the local file system in a non-contiguous way [10].

Timestamp 8exec increasing time is related to multicore calculation overhead. When multiple cores are processing different sets of data, the shared resource becomes a performance bottleneck, if the bandwidth is not high enough to support the multiple cores [13] [12] [3] .

Observe that 6plot and 9write synchronization time increases from 8 cores running in the same machine environment to 1 per machine environment. The reason is that, in the first environment, the disks are located on different machines and, in the second environment, the disks are located in the same machine and that synchronization overhead increases when disks are located in different machines due to network traffic and other reasons.

We conclude that the use of all cores in a node causes a reduction in performance, with greater impact in the output operations and in timesteps calculation performance, therefore we need to investigate multicore memory contention performance in our application for both real and virtual memory access.

#### 4.2.2 Parallel File system performance evaluation

This test evaluates the OLAM I/O operation performance improvement on a parallel file system multicore platform. We execute this experiment on the cluster ICE, at the Institute of Informatics of the Federal University of Rio Grande do Sul with NFS file system and LUSTRE [6] parallel file system. The Paralllel filesystem is built by the hard disk on computing nodes, storing data on 2 nodes/machine. The switch configuration is 16 auto-negotiating 10BASE-T/ 100BASE-TX ports configured as auto MDI/MDIX. Wirespeed performance across all ports Store-and-forward switching.Auto-negotiation of port speed and duplex IEEE 802.3x full-duplex flow control. IEEE 802.1p Class of Service/Quality of Service (CoS/QoS) on egress and 4 hardware queues per port.

![](_page_4_Figure_10.png)

**Figure 4. OLAM speed-up environments: LUSTRE 8 cores running on 1 machine each, LUSTRE 8 cores running on the same machine and NFS 8 cores running on the same machine.**

Figure 4 presents OLAM speed-up for three ICE platform environments: LUSTRE 8 cores running on 1 machine each, LUSTRE 8 cores running on the same machine and NFS 8 cores running on the same machine.

Figure 4 shows that OLAM speedup on ICE NFS file system with 8 cores running on the same machine environment is close to ICE LUSTRE parallel file system with 8 cores running on the same machine. This figure also shows that as we decrease the number of nodes for ICE LUSTRE parallel file system, the performance improves for OLAM application. These results indicate that the parallel file system, as configured in our system, is not a viable alternative to improve OLAM application I/O performance on a multicore environment.

As shown in related works section, there are several reasons for these results. First the I/O challenge for current parallel file system is to support highly concurrent metadata accesses generated by multiple cores[2]. Also, parallel file systems are increasingly specialized to extract the highest possible performance for large I/O operations[10], while OLAM application uses many small files. Finally, OLAM parallel processes issue contiguous I/O requests individually and simultaneously. Therefore I/O requests are handled by the local file system in a non-contiguous way generating performance degradation that is even more critical in parallel file systems [10].

# 5 Conclusions and Future Works

This paper evaluates the performance of the Ocean-Land-Atmosphere Model (OLAM) on a multicore cluster environment. Our experiments demonstrate that the scalability of the system is limited by output operations performance. We also demonstrate that one of the reasons that generates output operations overhead is the low capacity of the multicore system in providing high aggregate I/O throughput for supporting highly concurrent access rates. Furthermore, overhead of the I/O operations are aggravated by the OLAM workload pattern which access a large number of small files that effects few write operations written in distinct archives.

We conclude that using many cores in the same node of a multicore system results in reduction of performance, generating greater impact in the output operation performance. Therefore, in order to scale on a high performance computing systems for those scientific applications the multicore I/O bottleneck needs to be resolved. Also, our work shows that, on a multicore environment, the scalability is not improved when I/O operations are running trough a parallel file system, neither running on local disks.

For future works we envision several directions. For instance, as seen in the work of [12], we plan to evaluate the optimal number of cores according to OLAM workload parameters.

We also intend to evaluate parallel I/O library from the work of [4], in order to reduce OLAM initialization file creation overhead, to evaluate the work of [9] in order to improve OLAM output write operation performance, to evaluate the techniques from the work of [2] in order to optimize OLAM small file I/O access and to evaluate the work of [10] in order to have many simultaneously I/O requests gathered and buffered locally then arranged in a better order to be scattered through I/O nodes in parallel .

In other direction, we need to study multicore memory hierarchy contention in order to improve OLAM timesteps execution time performance.

# References

- [1] Adcroft, A. ,Hill,C.,Marshall, Representation of topography by shaved cells in a height coordinate ocean model. In *Man.Wea.Rev., pages 125,2293-2315,* 1997.
- [2] Carns, P., et all. Small-File Access in Parallel File Systems. In *Parallel and Distributed Processing*, IPDPS 2009.1530-2075 pages1 -11.,2009.
- [3] Datta, K., et all. Stencil Computation Optimization and Autotuning on State-of-the-Art Multicore Architectures In Conference on High Performance Networking and Computing Proceddings of the 2008 ACM/IEEE conference on Supercomputing Section Papers, Article n 4., 2008
- [4] Frings, W.,Wolf,F.,Petkov,V. Scalable massively parallel I/O to task-local files. In *Proceedings of the Conference on High Performance Computing Networking, Storage and Analysis.* http://doi.acm.org/10.1145/1654059.1654077, 2009.
- [5] Gropp, W. Et al. High Performance,portable implementation of the MPI Message Passing Interface Standart. In *Parallel Computing, v.22,n.6,pages789-828,* 1996.
- [6] LUSTRE home page. *http://www.lustre.org/*
- [7] Marshall,J.,Adcroft,A.,Hill,C.,Perelman,L.,Heisey,C. A finite-volume incompressible Navier-Stokes Model for Studies of Ocean on Parallel Computers. In *J. Geophys. Res., 102,n.C3, pages 5753-5766,* 1997.
- [8] Messinger,F.,Janjic,Z.,Nickovic,S.,Gavrilov,D.,Deaven,D.G. The step-mpountain coordinate:Model Description and performance for cases of alpine lee cyclogenesis and for a case of an Appalachian redevelopment. In *Mon. Wea. Rev., 116, pages 1493-1520,* 1998.
- [9] Nawab, A ., et all. Scalable I/O Forwarding Framework for High-Performance Computing Systems. In *Cluster Computing and Workshops, CLUSTER09. IEEE International Conferenc*, pages 1-10, 2009.
- [10] Ohta, K., Matsuba, H. And Ishikawa, Y. Gather-Arrange-Scatter: Node-Level Request Reordering for Parallel File Systems on Multi-Core Clusters In *2008 IEEE International Conference on Cluster Computing*, pages 336-341 , 2008.
- [11] Pielke, R.A., et al. A Comprehensive Meteorological Modeling System - RAMS. In *Meteorology and Atmospheric Physics. 49(1),* pages 69-91, 1992.
- [12] Sun, X., Byna, S.,Holmgren,D. Modeling Data Access Contention in Multicore Architectures. In *Parallel and Distributed Systems (ICPADS), 2009 15th International Conference,* pages 213-219, 2009
- [13] Shalf, J. Memory Subsystem Performance and QuadCore Predictions In *Presentation at NERSC User Group Meeting, September 17.* 2007.
- [14] Smirni, E. and Reed, D.A. Lessons from characterizing the input/output behavior of parallel scientific applications, In *Perform. Eval.*, vol. 33, no. 1, pages 27 - 44, 1998.
- [15] Walko, R.L., Avissar, R. OLAM: Ocean-Land-Atmosphere Model - Model Input Parameters - Version 3.0. In *Tech. Rep., Duke University , November* 2008.

