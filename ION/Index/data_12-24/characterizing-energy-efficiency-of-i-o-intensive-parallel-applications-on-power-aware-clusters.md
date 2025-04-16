# Characterizing Energy Efficiency of I/O Intensive Parallel Applications on Power-Aware Clusters

Rong Ge, Xizhou Feng *Dept. of Mathematics, Statistics, and Computer Science Marquette University Milwaukee, WI 53201, USA* {*rong.ge,xizhou.feng*}*@marquette.edu*

Sindhu Subramanya and Xian-he Sun *Dept. of Computer Science Illinois Institute of Technology Chicago, IL 60616, USA sindhu.subramanya@gmail.com, sun@iit.edu*

*Abstract*—Energy efficiency and parallel I/O performance have become two critical measures in high performance computing (HPC). However, there is little empirical data that characterize the energy-performance behaviors of parallel I/O workload. In this paper, we present a methodology to profile the performance, energy, and energy efficiency of parallel I/O access patterns and report our findings on the impacting factors of parallel I/O energy efficiency. Our study shows that choosing the right buffer size can change the energyperformance efficiency by up to 30 times. High spatial and temporal spacing can also lead to significant improvement in energy-performance efficiency (about 2X). We observe CPU frequency has a more complex impact, depending on the IO operations, spatial and temporal, and memory buffer size. The presented methodology and findings are useful for evaluating the energy efficiency of I/O intensive applications and for providing a guideline to develop energy efficient parallel I/O technology.

# *Keywords*-Energy efficiency; parallel I/O; access pattern;

# I. INTRODUCTION

Energy efficiency is now a primary concern in evaluating high performance computing (HPC) systems. As supercomputers reach petaflops (1015) per second, they consume vast amount of power. For example, the current top 1 supercomputer, the Jaguar system hosted in Oak Ridge National Laboratory, requires 7 megawatts in just powering. Without fundamental technology advancement, power consumption will be a critical limiting factor for future exascale supercomputers. Further, such enormous energy consumption translates to large electricity bill, reduces system reliability, and constrains future scalability. Arguably speaking, improving energy efficiency is a theme that affects today's major computing technology trends including green computing, server consolidation, multicore architecture and cloud computing.

In this paper, we study the energy efficiency of parallel I/O workload on power-aware clusters. While parallel I/O has been an active research area in HPC for over two decades, there are few published studies that seek to understand the energy efficiency of parallel I/O workload. However, as pointed out by the NSF data intensive computing program, the broad availability of digital datasets, coupled with increased capability and decreased cost of both computing and storage technologies, will lead to a new spectrum of HPC applications in which processing massive data is the dominant issue. Accordingly, understanding the energy footprint of different parallel I/O workload is critical for optimizing HPC software and hardware to make HPC more energy efficient for data intensive applications.

This paper makes three major contributions. First, it extends high-performance power-aware computing focusing on communication intensive applications to I/O intensive parallel applications. Second, it characterizes the performance, energy, and efficiency of different I/O access patterns under varying CPU frequencies on real systems. Third, we evaluate the effects of dynamic voltage and frequency scaling (DVFS) on parallel I/O workload. The framework and methodology presented in this paper can serve as a starting point and basis for developing power-aware parallel I/O technology.

We organize this paper as follows. In the next section, we briefly overview related work and motivation for this study. In Section III, we outline our methodology for characterizing and evaluating the energy efficiency of parallel I/O workload. Then, the detailed experimental results are presented and analyzed in Section IV, followed by summaries of our major findings and future research direction.

# II. RELATED WORK

The work presented in this paper are related to two areas of research, high-performance power-aware computing (HPPAC) and parallel I/O. HPPAC aims to improve energy efficiency of HPC systems for scientific and engineering applications. HPPAC uses power-aware components and dynamically schedules those component to different powerperformance modes that best fit the computation demands. Multiple power-aware components have been studied, including DVFS capable microprocessor, multi-speed hard disk [1], [2], [3], power-aware interconnection [4], and multi-status memory modules [5]. DVFS is widely supported by modern high-end microprocessors such as AMD Opteron and Intel Xeon CPU families, while the other power aware

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 21:39:24 UTC from IEEE Xplore. Restrictions apply.

components are rarely found in production systems and mainly studied with simulation,.

DVFS-based power aware approaches follow a common principle: scheduling the processors to a higher frequency for CPU intensive phases and workloads and to a lower frequency for non-CPU-bound phases and workloads. In the past, DVFS has been primarily exploited for three types of parallel workload: communication intensive applications [6], [7], memory-bound applications [8], and load imbalanced applications [7]. The power-aware speedup performance model [9] generalized the effects of DVFS on workload with varying memory accesses distributions across the entire memory hierarchy. There are few published studies on the energy efficiency of parallel I/O, particularly within the context of DVFS capable power-aware clusters. Energy efficient I/O research was mainly targeted at general purpose or embedded computing. Such research attempted to reduce disk energy consumption using multi-speed hard disks [1], [2] and/or data management [3].

We build our study upon previous work on parallel I/O access pattern characterization. The studies by Smirni et al [10] suggested cyclic I/O accesses with fixed data size are common, but the temporal and spatial spacings between requests across cycles are less regular. Nieuwejaar et al [11] observed that parallel workloads on looselycoupled high performance systems led to interleaved I/O access patterns and strided I/O requests with high spatial locality on I/O nodes. Recently, we have conducted a more complete study of data access patterns and their impact on overall performance [12]. We have developed a system of notations, called I/O signature, to describe the I/O data access characteristics of an application and have applied the I/O signature approach successfully in data prefetching and data layout [13], [14]. We believe that the I/O characteristics can be explored for energy efficient computing as well. In this paper, we focus our work on characterizing the energy efficiency of parallel I/O access patterns and evaluating the effects of DVFS on parallel I/O energy efficiency. To our best knowledge, this is the first work emphasizing parallel I/O energy efficiency that complements the HPPAC and parallel IO research described above.

#### III. METHODOLOGY

In this paper, we use an empirical experimental approach to characterize the energy efficiency of parallel I/O workload. The methodology comprises three components: 1) parallel I/O access pattern classification and generalization, 2) energy-performance profiling, and 3) energy efficiency metric selection.

# *A. Parallel I/O Access pattern*

Today's HPC systems usually adopt a network-based parallel I/O architecture [15]. Figure 1 illustrates a typical parallel I/O access of a common data file that is physically distributed in a cluster of hard drives. Studies showed the performance of parallel I/O access is multivariate, impacted by the parallel file system, the number of concurrent I/O clients, the client's I/O access patterns and parameters, etc.

![](_page_1_Figure_8.png)

Figure 1. An high level overview of parallel IO access.

While it's possible to study the impacts of all factors to the energy efficiency of parallel I/O accesses, we intend to limit our discussions mainly in parallel I/O access pattern as our first step toward energy efficient parallel I/O. Similar to previous parallel I/O characterization work [11], [16], we use the following four types of factors to identify parallel I/O access pattern.

Access type: How is data manipulated by the application? Possible types include read, write, seek, and read-modifywrite. We focus on read and write in this work and study other operations in the future.

Spatial spacing: What are the spatial distance between the data from two subsequent I/O requests of the clients? Common values include contiguous, simple strided, nested strided, and random strided. In this study, we focus on several regular spatial spacings and leave others in the future work.

Within the MPI-IO context in which all processes of a parallel application access the same data file, each data request can be identified using two parameters, file offset *o f f* p,i and data block size *size*p,i . Here p denotes the rank of a MPI process and i denotes the i th data request. The spatial spacing can be captured by different combinations of *o f f* p,i and *size*p,i . The value of *o f f*p,0 is usually defined as the displacement of client p.

- 1) Sequential and contiguous Access. With sequential accesses, the relation *o f f*p,i+1 ≥ *o f f*p,i holds for all
![](_page_1_Figure_15.png)

Figure 2. Contiguous access in a parallel application with 4 processes.

![](_page_2_Figure_0.png)

Figure 3. Simple strided accesses in a parallel application with 4 processes.

|  |  |  |  |  | . |  | . |  | . |  |  |  |  | ... | ... |  |  |  |  |  |  |  | . |  |  |  |  |  |  |  |  |  | . | . |  | . | ... | Controller of the control of the control of the control of the controlled | STATISTICS CONTRACTOR COLLEGION COLLEGION COLLEGION COLLEGION COLLEGION COLLEGION COLLEGION COLLEGION COLLEGION COLLEGION COLLEGION CONTRACTOR COLLEGION CONTRACTOR COLLECTION |  |  |  |  |  |  | Concession Concession L. |  |  |  |  |  | . | . |  |  |  |  | .. |  |  | ... |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| .. |  | . |  | . | .. | .. | .. |  |  |  |  |  |  |  |  |  |  | . |  | . |  |  |  |  |  |  |  | .. | Company of Concession Canadian Canada Company |  | Company of the control of the control of the county of the county of the county of |  |  |  |  |  |  | . |  |  |  |  |  |  |  |  |  |  | . |  |  | . | .. | Company of the company of | Controller of the control of the control of the control of the controlled |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | NAMERANE RESERVED BE REAL CREAT CONSULT CONSULT CONSULT CONTRACT C |  |  |  |  |  |
| 104 | C |  | 1 14 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

Figure 4. Nested strided accesses with six parallel processes. Within a stride, two subsets of processes: 0, 1, 2 and 3, 4, 5 repetitively request data in two separate segments respectively.

data requests. Consecutive or contiguous access is a special case of sequential access in which *o f f*p,i+1 = *o f f*p,i + *size*p,i , or the beginning offset of the next I/O request follows exactly the ending offset of the current I/O request. Previous studies suggested that contiguous read/write accesses dominate in parallel applications [11]. Figure 2 illustrates a contiguous access pattern with 4 MPI processes, in which *o f f*p,i and *size*p,i are constant and equal.

- 2) Simple Strided Access. Simple strided I/O is another common access occurred in may parallel applications, where each process of an application reads a column or block of data from a two-dimensional matrix stored in row-major order [11]. For simple strided access, *o f f*p,i+1 = *o f f*p,i+*stride*i and typically *stride*i = ∑p *size*p,i . Figure 3 provides a graphical view of simple strided access from a parallel application with 4 MPI processes.
- 3) Nested Strided Access. If we substitute each data request from a single client in Figure 3 with another level strided access by a group of clients, we observe nested strided access, as shown in Figure 4. The six processes are grouped into two subsets: {0,1,2} and {3,4,5}. The first subset requests data in the first half of the stride with two repetitions, and the second subset requests data in the second half of the stride. From the process point-of-view, each process accesses the data with an outer stride of 12 blocks, and an inner stride of three blocks. Many block algorithms in scientific applications exhibit nested strided access pattern including PUMMA algorithm [17]. Compared to the simple strided access with the same stride size, the processes with nested strided access have a smaller request data size but more requests.

Request data block size: How large is the data block accessed by the clients? The values may vary from several bytes to 10s megabytes.

Temporal spacing: How are data accessed across time

steps from the clients? Possible types include one time access, repeat access, or cyclic access. When the same process accesses the same block of data in the file more than once, repeat access occur. We focus on one time access and repeat access. Between two consecutive reads, there are maybe other file operations such as seek and write. As most file systems use cache for improved performance, if the requested data is still in the cache, the file system could use the cached data to serve the client. In this case, the subsequent reads take advantage of temporal locality and are less costly than the first read.

#### *B. Performance and Power Profiling*

We extend the Powerpack [18], [19] toolkit for profiling the energy efficiency of parallel I/O accesses. Power-Pack is a profiling framework designed for power-aware computing study. It consists of hardware for direct power measurement, a set of APIs and command line utilities to control the meters and computer system power/performance modes (e.g., CPU frequencies), and various data collection/fusion/analysis modules to automate the profiling and analysis process.

In this study, we insert a power meter between the AC power input of a compute node (profile host) in the HPC cluster under test and a wall power outlet. The power logs are recorded on a separate compute node (meter host) via a USB interface. The benchmarks record their own performance profiles locally and issue logging control commands to the meter host. We instrument the benchmarks so that they can log session labels and time stamps which map to the source code and/or power profile. After the benchmarks finish executing, PowerPack initiates a data fusion utility to merge both performance and power profiles to produce the energy, efficiency, and performance profiles with required data format.

#### *C. Metrics for Performance, Energy and Efficiency*

The performance of I/O access is normally quantified using latency and bandwidth. As bandwidth usually dominates the overall I/O access time for large data size, in this paper we use *aggregate bandwidth* (MB/s) or the total number of megabytes accessed by all processes per second as the primary measure of the parallel I/O performance.

The benchmark iteratively accesses a file and each time accesses an amount that equals to the allocated buffer size. Accumulatively, the benchmark requests a total amount of data from the file and records the total execution time, sustained bandwidth, and energy consumption. To compare the energy consumptions of different access patterns, we project the energy consumptions that are required to access a common file size (4GB in later results analysis), assuming the accessing time has a linear relationship to the number iterations for a given buffer size. We use *Joule* as the unit of energy. We also note that the number of iterations in a test must be large enough to ensure the benchmark run sufficiently long time for accurate power profiling.

There is no established objective metric for measuring the energy efficiency of parallel I/O access due to the interactive relation between performance and energy. Higher performance usually costs more energy and less energy would sacrifice performance. As a reasonable tradeoff, we choose *bandwidth per watt* as the efficiency metric in our later discussions. We derive the average achieved bandwidth per watt power for a test by dividing the total amount of data accessed by the total energy consumed.

# IV. EXPERIMENTAL RESULTS

# *A. Experiment Setup*

We conduct our experiments on a 9-node power-aware cluster with gigabit ethernet. Each node of the cluster has dual AMD Opteron quad-core 2380 processors running CentOS 5.3 Linux. All the processor cores support individual DVFS capability and can be scheduled among four frequencies: 0.8GHz, 1.3GHz, 1.8GHz, and 2.5GHz. Each core has a 64KB L1 instruction cache, a 64KB L1 data cache, and a unified 512KB L2 cache. The four cores on the same chip share one 6MB L3 cache.

The cluster is configured to use NFS file system for shared storage across the cluster. The underlying main storage on the master node is three Western Digital WD7500AYPS Raid Edition 7200rpm SATA Hard Drive with RAID-5 configuration. This hard drive model has 750GB capacity, 16MB Data Cache, and a maximum 3GB/s buffer to host transfer speed.

We use PIO-Bench [20] as the benchmark tools to generate the parallel I/O access patterns with various parameters. We made some modifications on the public available PIO-Bench to serve our purpose. We also inserted new code segments to integrate with the PowerPack power-energy profiling environment. PIO-bench uses MPI-IO [21] to perform parallel I/O operations. In our experiments, MPICH2 version 1.0.7 is chosen as the MPI I/O implementation.

Following the methodology described in Section III-C, we report our results of each access pattern in bandwidth, energy consumption of accessing 4GB data, and derived energy efficiency under different CPU frequency. Unless explicitly stated, we run all the test cases on a single compute node using all 8 cores.

# *B. The Efficiency of Parallel Contiguous Read*

As our first case study, we profile the energy-performance efficiency of parallel contiguous read with varying request data size under different CPU frequency. Figure 5 shows the performance, energy, and efficiency of parallel contiguous reading using 8 MPI processes. In each figure, x-axis represents CPU frequency and y-axis represents bandwidth, energy, and energy efficiency respectively. We plot the profiles of each buffer size (i.e., the data size of each access request) with a separate line. We observe the following trends:

- (1) The parallel I/O bandwidth increases substantially with the request buffer size. For the set of buffer sizes we have tested, a larger buffer size always leads to a larger bandwidth, less energy, and higher efficiency. By increasing the buffer size from 512 bytes to 64K bytes, the energy efficiency increases by 30 times from 9.2 MB/Joule to 267.5 MB/Joule. Nevertheless, we also observe the returns of the bandwidth and energy efficiency diminish as buffer size increases.
- (2) For a given buffer size, increasing CPU frequency only slightly increases bandwidth. For example, scaling CPU frequency from 1.3GHz to 2.5GHz only gains 5.6% additional bandwidth.
- (3) Unlike bandwidth, energy consumption doesn't monotonically increases with CPU frequency. For example, when the buffer size is larger than 4KB, scaling up CPU frequency from 0.8GHz to 1.3GHz leads to reduced energy consumption and further scaling up to 1.8GHz and 2.5GHz leads to slight increases in energy consumption.
- (4) For most buffer sizes, 1.3GHz achieves the highest efficiency for parallel contiguous read. Comparing to 2.5GHz, it improves energy efficiency by up to 13% with less than 5% bandwidth loss.

These observations provide several important hints for optimizing parallel I/O energy efficiency of contiguous read. First, they imply application optimization such as choosing the right buffer size and packing small data request to a larger request might be the most effective way to improve parallel I/O energy efficiency. Second, the results indicate that intelligent DVFS scheduling could save energy and improve energy efficiency, though the amount of benefits is not significant (in the best case, it could save up to 13% energy). Third, the results suggest that lowest frequency does not always leads to minimum energy and highest energy efficiency.

![](_page_4_Figure_0.png)

(c) Efficiency

Figure 5. The effects of frequency scaling and buffer size on energy efficiency of parallel contiguous read.

#### *C. The Efficiency of Parallel Strided Read*

Figure 6 shows the energy-performance profiles for parallel simple strided read access. The profiles look similar to those of contiguous read access but do have several key differences.

First, unlike contiguous read access that exhibits a regular pattern, simple strided access shows an irregular pattern in term of the bandwidth vs. buffer size. The sustained bandwidth doesn't monotonically increase with the buffer size. The figure shows buffer size 8KB outperforms buffer size16KB, and buffer size 32KB outperforms buffer size 64KB.

Second, for the same buffer size and the same CPU frequency, simple strided access usually has a lower bandwidth, higher energy consumption, and lower energy efficiency in

![](_page_4_Figure_7.png)

Figure 6. The effects of frequency scaling on simple strided read with various buffer size.

comparison with contiguous read. The efficiency loss due to strided access could be as large as 250%. However, there are some exceptions. Buffer sizes of 8KB and 32KB in simple strided read achieve higher bandwidth and higher energy efficiency than in contiguous read access. We believe these exceptions are related to the characteristics of file systems but need to further investigate in our following studies.

Third, several buffer sizes (e.g., 2 KB and 64 KB), when CPU is running at 1.3GHz or 0.8GHz, not only consume less energy but also achieve higher bandwidth. The highest frequency (2.5GHz) does not necessarily lead to highest bandwidth with highest energy consumption. Further data analysis indicates DVFS can improve energy efficiency (MB/Joule) by a significant amount (up to 28% for 64KB buffer size by running at 0.8GHz).

![](_page_5_Figure_0.png)

(c) Efficiency

Figure 7. The effects of frequency scaling on nested strided read with various buffer size.

The profiles of nested strided read access, as shown in Figure 7, also reveal some different trends. First, smaller buffer sizes achieve smaller bandwidth and larger buffer sizes achieve comparable or even larger bandwidth in nested strided access than in contiguous read. Second, the profiles also shows buffer size "out-of-order" regarding to their corespondent bandwidth and efficiency: the 8KB buffer size leads to better performance than 16KB buffer size. For most cases, running at 1.3GHz seems to be most energy-efficient for nested strided access.

#### *D. The Efficiency of Parallel Contiguous Write*

As shown in Figure 8, the energy-performance profiles of parallel contiguous write are more complex than those of parallel contiguous read access. In general, the bandwidth and energy efficiency of write access are less than one

![](_page_5_Figure_6.png)

Figure 8. The effects of frequency scaling on contiguous write with various buffer size.

half of their read counterpart. Also, all measures including bandwidth, energy, and efficiency no only depend on both request size and CPU frequency but also their interactions. This fact is more evident for the test cases with 16 KB and 32 KB buffer sizes, where bandwidth and efficiency drop significantly when the processors scale from 1.3GHz to 1.8GHz. Similar to parallel read access (either contiguous or strided), increasing buffer size usually results in less energy consumption and higher energy efficiency. Among test cases we have studied, 1.3GHz seems to be most energy efficient than other three frequencies.

#### *E. The Effects of Temporal Spacing*

For parallel I/O access with high temporal locality, we expect improved performance and energy efficiency. In this section, we use contiguous re-read and re-write access

![](_page_6_Figure_0.png)

(c) Efficiency

Figure 9. The effects of frequency scaling on contiguous re-read with various buffer size.

to examine the effects of temporal locality. As shown in Figure 9, contiguous re-read almost triples the bandwidth of contiguous single read and delivers up to 150MB/s bandwidth, which is roughly the maximum network bandwidth of the test cluster. Further, the bandwidth in contiguous reread is more responsive to CPU frequency than contiguous single read. For example, as the CPU frequency scales from 1.3GHz up to 2.5GHz, the bandwidth with 64 KB buffer size increases by 20% for contiguous re-read compared to 10% for contiguous single read.

Similar to re-read, contiguous re-write almost doubles the bandwidth of contiguous single write. However, as shown in Figure 10 the changes of bandwidth and efficiency with buffer sizes are not regular, indicating there exists an optimal buffer size that delivers highest energy efficiency. Moreover,

![](_page_6_Figure_5.png)

Figure 10. The effects of frequency scaling on contiguous re-write with various buffer size.

the bandwidth and energy vary with CPU frequency more regularly than single write access. For example, as the frequency increases from 1.3GHz to 1.8GHz, the bandwidth with 16KB buffer size monotonically increases in re-write, in comparison with dropping below 10MB/s from above 20MB/s in single write.

# V. SUMMARY

Though both energy efficiency and parallel I/O are critical to scalable high performance computing systems, there is little empirical data on the energy efficiency characteristics of parallel I/O workload. In this paper, we have outlined our methodology of characterizing energy-efficiency of parallel I/O access patterns and reported our results and observations collected on a state-of-art power-aware cluster.

These results clearly show the characteristics and trends of the energy-performance efficiency of typical parallel I/O access patterns found in practical applications. We observe that buffer size and CPU frequency can significantly impact energy efficiency of I/O accesses, and their interactions are complicated, depending on the spatial and temporal parameters of the accesses. Overall, the results in this study suggests application or system level optimization is able to greatly increase parallel I/O energy efficiency. Nevertheless, such optimization requires tailoring the computing frequency and memory buffer size to the application data access characteristics.

This work is a starting point of our energy-efficient parallel I/O research and leads to many interesting questions waiting to be explored. Application-oriented techniques would enable major applications in computing centers to better use energy. Analytical models would be useful to evaluate the energy efficiency of I/O intensive applications, and to guide the development of energy efficient file storage facilities and system support services in high performance computing.

### REFERENCES

- [1] S. Gurumurthi, A. Sivasubramaniam, M. Kandemir, and H. Franke, "Drpm: Dynamic speed control for power management in server class disks," in *The 30th Annual International Symposium on Computer Architecture*, San Diego, California, 2003, p. p. 169.
- [2] E. V. Carrera, E. Pinheiro, and R. Bianchini, "Conserving disk energy in network servers," in *the 17th International Conference on Supercomputing*, 2003.
- [3] Q. Zhu, Z. Chen, L. Tan, Y. Zhou, K. Keeton, and J. Wilkes, "Hibernator: Helping disk array sleep through the winter," in *the 20th ACM Symposium on Operating Systems Principles (SOSP'05)*, 2005.
- [4] V. Soteriou, N. Eisley, and L.-S. Peh, "Software-directed power-aware interconnection networks," *ACM Trans. Archit. Code Optim.*, vol. 4, no. 1, p. 5, 2007.
- [5] X. Fan, C. S. Ellis, and A. R. Lebeck, "The synergy between power-aware memory systems and processor voltage scaling," Department of Computer Science Duke University, Tech. Rep. TR CS-2002-12, 2002.
- [6] R. Ge, X. Feng, and K. W. Cameron, "Improvement of power-performance efficiency for high-end computing," in the *first HPPAC workshop in conjection with 19th IEEE/ACM International Parallel and Distributed Processing Symposium (IPDPS)*, Denver, Colorado, 2005.
- [7] N. Kappiah, V. W. Freeh, and D. K. Lowenthal, "Just in time dynamic voltage scaling: Exploiting inter-node slack to save energy in mpi programs," in *IEEE/ACM Supercomputing 2005 (SC '05)*, 2005.

- [8] C.-H. Hsu and U. Kremer, "The design, implementation, and evaluation of a compiler algorithm for cpu energy reduction," in *PLDI '03: Proceedings of the ACM SIGPLAN 2003 conference on Programming language design and implementation*. New York, NY, USA: ACM, 2003, pp. 38–48.
- [9] R. Ge and K. W. Cameron, "Power-aware speedup," in *IEEE International Parallel and Distributed Processing Symposium (IPDPS) 2007*, Long Beach, CA, 2007.
- [10] E. Smirni and D. Reed, "Lessons from characterizing the input/output behavior of parallel scientific applications," *Performance Evaluation*, vol. 33, no. 1, pp. 27–44, 1998.
- [11] N. Nieuwejaar, D. Kotz, A. Purakayastha, C. S. E. Y, and M. B. Z, "File-access characteristics of parallel scientific workloads," *IEEE Transactions on Parallel and Distributed Systems*, vol. 7, pp. 1075–1089, 1996.
- [12] S. Byna, X. Sun, R. Thakur, and W. Gropp, "Automatic memory optimizations for improving MPI derived datatype performance," *Lecture Notes in Computer Science*, vol. 4192, p. 238, 2006.
- [13] S. Byna, Y. Chen, X. Sun, R. Thakur, and W. Gropp, "Parallel I/O prefetching using MPI file caching and I/O signatures," in *Proceedings of the 2008 ACM/IEEE conference on Supercomputing*. IEEE Press, 2008, pp. 1–12.
- [14] X.-H. Sun, Y. Chen, and Y. Yin, "Data layout optimization for petascale file systems," in *PDSW '09: Proceedings of the 4th Annual Workshop on Petascale Data Storage*. New York, NY, USA: ACM, 2009, pp. 11–15.
- [15] R. Watson and R. Coyne, "The parallel I/O architecture of the high performance storage system (HPSS)," in *Proceedings of the Fourteenth IEEE Symposium on Mass Storage Systems (MSS'95)*, vol. 1051, 1995.
- [16] P. Crandall, R. A. Aydt, A. A. Chien, and D. A. Reed, "Input/output characteristics of scalable parallel applications," in *in Proceedings of Supercomputing 95*. Press, 1995.
- [17] J. Choi, J. J. Dongarra, and D. W. Walker, "Pumma: Parallel universal matrix multiplication algorithms on distributed memory concurrent computers," in *Concurrency: Practice and Experience*, vol. 6(7), 1994, pp. 543–570.
- [18] R. Ge, X. Feng, S. Song, H.-C. Chang, D. Li, and K. W. Cameron, "Powerpack: Energy profiling and analysis of highperformance systems and applications," *IEEE Transactions on Parallel and Distributed Systems*, vol. 99, no. 1, accepted.
- [19] X. Feng, R. Ge, and K. Cameron, "Power and energy profiling of scientific applications on distributed systems," in *19th International Parallel and Distributed Processing Symposium (IPDPS 05)*, Denver, CO, 2005.
- [20] F. Shorter, "Design and analysis of a performance evaluation standard for parallel file systems," Master's thesis, Clemson University, 2003.
- [21] R. Thakur, W. Gropp, and E. Lusk, "On implementing MPI-IO portably and with high performance," in *Proceedings of the sixth workshop on I/O in parallel and distributed systems*. ACM New York, NY, USA, 1999, pp. 23–32.

