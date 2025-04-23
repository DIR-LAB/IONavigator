# Modeling the Impact of System-level Parameters on I/O Performance of HPC Applications

Debasmita Biswas∗ , Arnab K. Paul† , Sarah Neuwirth‡ and Ali R. Butt∗

∗*Virginia Tech, USA*, {debasmita17, butta}@vt.edu

†*BITS Pilani, K K Birla Goa Campus, India*, arnabp@goa.bits-pilani.ac.in

‡ *Johannes Gutenberg University Mainz, Germany*, neuwirth@uni-mainz.de

*Abstract*—Modern High Performance Computing (HPC) workloads prioritize data, challenging storage systems to meet rising I/O demands. The network's role in inter-node communication and data transfer significantly impacts overall application performance. Our study systematically examines bandwidth and latency variations in CephFS due to diverse I/O patterns. We formalize latency, bandwidth, I/O size, and blockto-file size ratio relationships and train a model for predicting bandwidth and estimating latency in similar I/O workloads, offering valuable insights into optimizing HPC storage.

*Index Terms*—System-level Parameters, I/O Performance, Access Patterns, Prediction, HPC, Bandwidth, Latency

## I. INTRODUCTION

As data-driven science grows, modern HPC applications have become data-intensive, straining HPC storage systems. I/O scalability lags behind computing power growth, causing I/O to bottleneck data-intensive applications needing high throughput and low latency. Networking is crucial for node communication and data transfer speed in storage clusters.

HPC storage relies on a parallel file system or object store, communicating via the network layer. This close interaction between I/O and networking often hampers application performance, yet limited research has holistically explored their mutual impact [9]. While network visualization tools like Wireshark offer real-time networking statistics, they do not directly relate to I/O speed. Other tools such as Netperf, iPerf, IOR [6], HACC-IO [7], FileBench [5] and MDTEST [6] focus on specific aspects but lack a comprehensive solution for real-time insights into storage system I/O and network latency during HPC application execution.

To fill this gap in the literature, we quantitatively study the interaction of I/O and network together. We are able to gain valuable insights into how network latency is related to file system parameters on the client side. For this work, we target small-scale academic clusters equipped with commodity hardware and the Ceph Distributed Object Storage [1]. We perform extensive experiments involving different data access patterns, orderings in files, thread counts, and block sizes. Specifically, we make the following contributions:

- 1) *I/O Behavior Study: We investigate the relationship between workload parameters, network, and storage performance with respect to the Ceph file system.*
- 2) *Mathematical Model: We work on an observationdriven mathematical model that correlates workload*

*parameters with bandwidth and latency for an application run. An important observation is that the I/O transfer size is directly proportional to the product of bandwidth and latency achieved by an application.*

- 3) *Evaluation: We evaluate our model on different cluster configurations, network link speeds, and workloads mimicking the real-world applications, such as a video server and a database.*
## II. BACKGROUND AND MOTIVATION

HPC workloads each have specific performance needs. While some demand high throughput or low latency, emerging workloads exhibit random, small patterns, straying from sequential norms. Despite networks' impact on storage bandwidth, slow I/O remains a bottleneck, affecting application throughput. To investigate our hypothesis, we perform benchmarks at both the storage and network levels that aim to provide insights into the disparity between the anticipated and actual parallel I/O performance at the application level.

## A. *Selected Benchmarks*

*Interleaved or Random (IOR)* assesses the performance of parallel file and storage systems in handling different data access patterns, often seen in high-performance computing. It measures throughput, latency, and data integrity, and allows users to configure various parameters, including file size, access pattern, block size, and number of processes.

*FileBench* is a benchmarking tool designed to evaluate the performance of file systems by simulating real-world workloads. It provides customizable workloads, measuring file system behavior under various conditions, such as read and write operations, metadata operations, and mixed workloads.

*Netperf* is a network performance testing tool used to measure the performance of networking protocols and connections. It evaluates network bandwidth, latency, and throughput by simulating various network communication scenarios. As baseline experiments, we ran the bulk transfer tests, i.e., TCP STREAM between the nodes in our CephFS cluster.

## B. *Ceph Object Store*

Ceph [1] is an open-source, distributed storage system designed for scalable and fault-tolerant data storage. Its key components include: Ceph Object Store (RADOS), Ceph OSD (Object Sotrage Daemon), Ceph Monitor (MON), Ceph Metadata Server (MDS), and Ceph Client. Ceph's Reliable

![](_page_1_Figure_0.png)

Fig. 1: I/O performance of CephFS testbed (see Sec. VI) with 10 Gb Ethernet link and a file size of 16 GiB.

Autonomic Distributed Object Store (RADOS) is the fundamental storage layer, managing data as objects across a server cluster, ensuring high availability. Ceph OSDs are responsible for data storage, replication, and fault tolerance. MON maintains cluster configuration, aiding data placement and recovery decisions. The Ceph Clients prove interfaces for applications to access data in the cluster. Finally, the MDS enables CephFS, a POSIX-compliant distributed file system, by managing metadata and facilitating file access. CephFS offers scalable and reliable file storage. It is suitable for a wide range of applications, including those in high-performance computing and cloud environments, where flexible and efficient file storage and access are crucial.

## C. *Conclusions from Baseline Performance Metrics*

When performing the baseline experiments, it became clear that the throughput lags behind the maximum attainable throughput between the cluster nodes, as shown in Figure 1. This indicates a potential for improvement for the overall cluster I/O of the storage system. To evaluate possible ways to exploit the available network potential and optimize I/O speed, in this work we (a) investigate the network behavior by testing variable network settings to complement the storage system architecture; (b) evaluate and analyze the characteristics of the workloads hosted on the storage system.

## III. RELATED WORK

I/O patterns exhibited by application workloads are changing rapidly, read operations can be dominant in new and emerging workloads like in machine learning. Specific applications may require lower latency, even at the cost of throughput, whereas others may prioritize throughput with a high latency. Shan et al. [2] perform a thorough study of predicting bandwidth through the use of IOR, by configuring it to mimic several other benchmark applications. However, the paper claims that sequential-write patterns are the overwhelming majority in HPC workloads and does not discuss performance prediction for random file access patterns. Several recent studies have addressed changing I/O characteristics of newer workloads. Costa et al. [3] adopt a machine learning assisted approach to detect I/O variability in repetitive jobs. However, they do not take into consideration latency variation and its effects on I/O. Zhu et al. [4] propose an automated workflow to analyze application specific I/O behavior of systems but do not further examine the bandwidth/latency trade-off.

## TABLE I: MPI file access patterns and configurations.

| File Access | Ordering | Description |
| --- | --- | --- |
| single-shared | sequential | All MPI processes perform I/O operations on |
| file (SSF) |  | a single file, accessing sequentially ordered |
|  |  | offsets within a file. |
| single-shared | random | All MPI processes perform I/O operations |
| file (SSF) |  | on a single file, accessing randomly ordered |
|  |  | offsets within a file. |
| file-per | sequential | Each MPI process performs I/O operations on |
| process (FPP) |  | a unique file, accessing sequentially ordered |
|  |  | offsets within a file. |
| file-per | random | Each MPI process performs I/O operations |
| process (FPP) |  | on a unique file, accessing randomly ordered |
|  |  | offsets within a file. |

# IV. SYSTEMATIC ANALYTICAL STUDY OF I/O BEHAVIOR

Below, we examine the impact of changing storage and network parameters on the I/O on our small CephFS testbed (refer to Section VI) from an application layer perspective.

## A. *I/O Transfer Size Variation*

The I/O transfer size controls the amount of data buffered for each I/O call directed to the system. Depending on the file access and ordering patterns shown in Table I, the I/O transfer size affects the achieved bandwidth and/or latency of a read or write operation. Figure 2 shows the benchmark results for scaling the I/O transfer size for a total file size of 16 GiB. Since the results for random and sequential reads and writes are similar for SSF, they have been omitted to save space. We make the following observations:

*Sequential Read (SSF):* The best performance in terms of both bandwidth and latency was achieved with the lowest transmission size, i.e. 4 KiB. The latency increases linearly with increasing values of the I/O transfer size. The trade-off between latency and bandwidth is unfavorable, as the highest bandwidth was observed for the lowest transfer size.

*Sequential Write (SSF):* The increase in latency is proportional to the change in I/O transfer size, while the bandwidth changes are negligible. Thus, increasing the transfer sizes may not result in improved write bandwidth for the system.

*Random Read (SSF):* Significant bandwidth gains were observed when increasing the transfer size for random reads. Bandwidth and latency increase non-linearly with increasing I/O transfer size. Latency increases by a factor of the increase in I/O transfer size from 512 KiB, while the bandwidth gains slow down. Hence, it is possible to determine a I/O transfer size that is optimal for a particular application.

*Random Write (SSF):* Latency increases with the change in I/O transfer size without significant bandwidth increase, suggesting that random writes to a single shared file may not benefit from the change in I/O transfer size.

*Sequential Read (FPP):* Latency increases when the I/O transfer size is increased without a benefit for the bandwidth. This suggests that workloads that perform sequential reads on a single shared file may not experience performance benefits from increasing the I/O transfer size.

*Sequential Write (FPP):* Latency increases linearly with change in I/O transfer size without significant bandwidth gain, indicating that sequential writes for file per process may not benefit much from varying the I/O transfer size.

![](_page_2_Figure_0.png)

1000

$\begin{array}{c}\text{2000}\\ \text{Transfer Size}\end{array}$

Fig. 3: Effects of concurrent job runs on bandwidth and latency (bandwidth in MiB/s, latency in seconds, transfer size in KiB, *ssf:* singled-shared-file, *fpp:* file per process, c1: client1, c2: client2).

TABLE II: Job Configuration for Concurrency Tests

|  | Client1 | Client2 |  | Client1 | Client2 |
| --- | --- | --- | --- | --- | --- |
| 1 | ssf,random | ssf,sequential | 4 | fpp,random | ssf,random |
| 2 | ssf,random | fpp,sequential | 5 | ssf,sequential | fpp,sequential |
| 3 | fpp,random | fpp,sequential | 6 | fpp,random | ssf,random |

*Random Read (FPP):* The latency and bandwidth increase with increasing I/O transfer size for random reads on file-perprocess. When using larger I/O transfer sizes and simultaneously increasing the bandwidth, there is a significant increase in latency. This suggests that it may be beneficial to find an optimal I/O transfer size that balances bandwidth and latency requirements for specific applications.

*Random Write (FPP):* Latency increases linearly with I/O transfer size, with negligible impact on write bandwidth. Thus, applications may not experience any performance benefits from increasing the I/O transfer size, but may benefit from lower latency without compromising bandwidth.

#### B. *Effect of Varying Block Sizes*

Block size refers to the contiguous portion of data that is written to a file system. A smaller block size can be advantageous for applications that perform small file accesses because it does not waste space in the file system. Larger blocks, meanwhile, provide better performance for larger data accesses. Our experiments show that the ratio of block size to file size is proportional to the product of bandwidth and latency for a workload run. We observe a change in latency that is proportional to the change in the file-to-block size ratio, while the average bandwidth remains roughly the same when all other factors remain constant.

## C. *Effect of Concurrent Workloads*

To measure the behavior of the file system under multiple workloads, we launched jobs from two CephFS clients. The job configurations are shown in Table II. Figure 3 shows the trend of bandwidth and latency change in case of concurrency, which is consistent with what has been observed for single-client runs – we observe reduced performance for single workloads, but overall better system utilization.

## D. *Effect of Varying TCP Socket Buffer Size*

Contrary to our assumption, we did not see any non-trivial variations in bandwidth or latency when we changed the TCP socket buffer settings. We repeated all our experiments with TCP settings for a socket buffer size of 256 MiB, but the values for bandwidth and latency remained similar and showed the same trends. This could indicate that memory bandwidth is not affected by the network settings, but by the I/O subsystem. So, to better exploit the potential of the network, we need to further investigate the I/O configurations and optimize them for improved performance.

## V. MODELING SYSTEM-LEVEL PARAMETERS

Using our data-driven observations as described in Section IV, we can formulate the relationship between the storage parameters of IOR and the latency of the system. The relationship applies to any system, access pattern, file arrangement, and number of threads started by a workload. We further tested this relationship against the FileBench [5] benchmark results to verify its effectiveness, and it remained valid. The relationship can be defined as follows:

$$\left(\frac{totalSize}{blockSize}\right)\times Size_{I/O}=bandwidth\times latency\tag{1}$$

where, totalSize is the total amount of data read or written to the system, blockSize is the size of a contiguous chunk of data in a file that an application operates on, SizeI/O is the I/O transfer size (i.e. amount of data that an application transfers in a single I/O call), bandwidth is the maximum amount of data that the file system processes in unit time, and latency is the system response time for a single I/O call, dependening on the internal network communication speed of the storage system. In the context of IOR, the equation can also be expressed as follows:

CountS × numP roc × SizeI/O= latency × bandwidth (2)

![](_page_3_Figure_0.png)

Fig. 4: Logarithmic Regression (RMSE: 22206984.67) vs Random Forest Regressor (RMSE: 8299118.73) predictions against observed bandwidth (bytes) values.

where, CountS is the number of segments, ie., number of contiguous blocks of data in a file that each process can operate upon. For a workload where the aggregate file size is equal to the block size, the transfer size is equal to the product of latency and bandwidth. This means that a smaller increase in bandwidth relative to an increase in transfer size will increase bandwidth. The slope of latency versus increase in transfer size can depend on access patterns and ordering in a file, as is evident in our discussion in Section IV.

Our observations suggest that there are patterns in bandwidth and latency that change and are predictable as I/O parameters change. Latency can change linearly or nonlinearly depending on access and operations performed. Bandwidth shows a non-linear change, if any. We test logarithmic and random forest regression models to predict bandwidth as a function of I/O transfer, block and file sizes, access, and order in files. Random Forest uses an ensemble model with multiple decision trees for prediction and performs better than logarithmic regression, as shown in Figure 4 for random reads and the file-per-process access pattern.

## VI. EVALUATION

We evaluate our proposed model on the CephFS, hosted on our on-premises Ceph Distributed Object Storage Cluster running on 8 host machines, all running Rocky Linux 8. Each server is equipped with AMD FX-8320E 8-Core processor, operating at a frequency of 3.2 GHz, and 500 GB SSD.

## A. *Validity of Mathematical Relationship and Trends*

We tested the legitimacy of the Equation 1 by testing the bandwidth and latency values obtained upon running the IOR benchmark on our cluster. The equation held true across all I/O patterns, file to block size ration and transfer sizes.

We also tested the validity of the trends in latency and bandwidth for varying I/O transfer sizes across all file access, ordering patterns and operations performed by changing Ethernet link speed on one of the OSD nodes. While it changed the latency and bandwidth observed for the same workload runs across the two FS configurations, the trend in change of latency and bandwidth with change in I/O transfer sizes and storage parameters remained the same.

## B. *Optimization on Real-world Applications*

We evaluated the performance of CephFS with the FileBench workload oltp.f, which emulates real database behavior and is throughput-sensitive. oltp.f is based on the Oracle 9i I/O model and is characterized by random reads and writes with a default I/O size of 2 KiB. We achieved a 60x throughput improvement using an I/O size of 512 KiB, which was recommended by our model, with an approximate 6x latency increase for a file set size of 10000 MiB. The FileBench workload videoserver.f, which emulates the behavior of video servers when writing, replacing, and serving video files, was used to evaluate real-world latency-sensitive application workloads. At the recommended read I/O size of 4k compared to the default size of 256K, we achieved 500x lower application latency without compromising throughput.

## VII. CONCLUSION

In this paper, we have systematically analyzed and established a general mathematical relationship between I/O transfer size, bandwidth, and latency for arbitrary read and write operations. We have benchmarked and predicted bandwidth/latency for different I/O transfer sizes, for different data access patterns and file layouts to help users make informed decisions about application-specific bandwidth/latency tradeoffs and improve I/O performance.

## ACKNOWLEDGMENT

This work is sponsored in part by the NSF under the grants: 2106634, 1919113, and 2312785. Further, this work is sponsored in part by the grants BBF/BITS(G)/FY2022- 23/BCPS-123, and BPGC/RIG/2021-22/06-2022/02.

## REFERENCES

- [1] Sage A. Weil, Scott A. Brandt, Ethan L. Miller, Darrell D. E. Long, and Carlos Maltzahn. 2006. Ceph: a scalable, high-performance distributed file system. In Proceedings of the 7th symposium on Operating systems design and implementation (OSDI '06).
- [2] H. Shan, K. Antypas and J. Shalf, "Characterizing and predicting the I/O performance of HPC applications using a parameterized synthetic benchmark," SC '08: Proceedings of the 2008 ACM/IEEE Conference on Supercomputing, Austin, TX, USA, 2008, pp. 1-12.
- [3] Emily Costa, Tirthak Patel, Benjamin Schwaller, Jim M. Brandt, and Devesh Tiwari. 2021. Systematically inferring I/O performance variability by examining repetitive job behavior. In Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis (SC '21).
- [4] Z. Zhu, S. Neuwirth and T. Lippert, "A Comprehensive I/O Knowledge Cycle for Modular and Automated HPC Workload Analysis," 2022 IEEE International Conference on Cluster Computing (CLUSTER), Heidelberg, Germany, 2022, pp. 581-588.
- [5] Vasily Tarasov, Erez Zadok, and Spencer Shepler. 2016. Filebench: A Flexible Framework for File System Benchmarking. login Usenix Mag. 41, 1 (2016).
- [6] "IOR Benchmark." https://github.com/hpc/ior. Accessed:05-15-2023
- [7] Klockwood, G. hacc-io. Retrieved from https://github.com/ glennklockwood/hacc-io Accessed:05-15-2023
- [8] Leo Breiman. 2001. Random Forests. Mach. Learn. 45, 1 (October 1 2001), 5–32. https://doi.org/10.1023/A:1010933404324
- [9] D. Biswas, S. Neuwirth, A. K. Paul and A. R. Butt, "Bridging Network and Parallel I/O Research for Improving Data-Intensive Distributed Applications," 2021 IEEE Workshop on Innovating the Network for Data-Intensive Science (INDIS), 2021, pp. 50-56.

