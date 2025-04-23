# Memory Hierarchy Aware I/O Scheduling Under Contention for Hybrid Storage Based HPC

Benbo Zha∗, Hong Shen∗†

∗School of data and computer science, Sun Yat-sen university, China †School of Computer Science, University of Adelaide, Australia Email: *zhabb@mail2.sysu.edu.cn, hongsh01@gmail.com*

*Abstract*—Scientific computing involved with handling enormous computation and processing huge volume of data poses a serious challenge to high performance computing (HPC). The significant progress of computational power further widens the historical gap between processing speed and storage latency. Introducing solid-state-drives (SSDs) as a burst buffer or cache to memory hierarchy in hybrid storage based HPC can effectively improve the I/O performance. Meanwhile, increasing the number of processes to get greater parallelism also can reduce the final execution time. However, these methods are unable to adequately utilize the system resources when there is competition for system resources like SSDs, I/O network. In this paper, we first analyze the effects of I/O congestion between different applications and SSDs contention between different processes. Then, a memory hierarchy aware I/O scheduling method, which is able to detect contentions and schedules I/O to relieve this situation, is proposed to improve overall I/O performance. The theoretical analysis and extensive experiments prove that our method is effective and efficient. The results from the real-world scientific simulations show this I/O scheduling technique achieves up to 20% execution performance improvement.

*Index Terms*—memory hierarchy, I/O scheduling, resource contention, hybrid storage, high performance computing

## I. INTRODUCTION

Scientific computing has already became an approach as one of the three pillars for science discovery along with theory and experiment. High performance computing (HPC) with high computational speed and huge storage capability give an opportunity to the scientific computing, such as scientific simulation, big data analysis. Meanwhile, the rapidly increasing volume of computation and data for scientific application like *computational fluid dynamic, quantum chromo dynamics, seismic simulation*, is widening the historical gap between processing power and storage performance. To mitigate this I/O bottleneck, most of HPC systems introduce solid-statedrives (SSDs), which are two orders of magnitude faster than traditional hard-disk-drives (HDDs) and have at least 10 times more space than DRAM [1], into its memory hierarchy. This kind of hybrid storage based HPC can obviously improve the performance of the storage system by simply using SSDs as a burst buffer or cache. But how to take full advantage of memory hierarchy to improve system performances like resource utilization and task completion time became a significant problem.

In addition, general scientific computing applications were executed on plenty of computing nodes to reduce the completion time. On each node there are several processes for computing same tasks. When many applications executed concurrently, contention will be caused on bottleneck resources like SSDs, I/O bandwidth. According to a report from the Intrepid system at Argonne [2], the congestion can cause up to a 70% decrease in the I/O performance of an application as shown in Fig. 1. The contention will be caused on SSDs, which is installed on compute nodes, when the number of processes in a node is too many. This kind of contention might cause 50% performance reduction and the proposed memory hierarchy based method can relieve this problem [3]. In this work, we further explore how to schedule I/O by utilizing memory hierarchy under contention to improve HPC system performance.

![](_page_0_Figure_10.png)

Fig. 1. I/O throughput decrease (percentage per application instance, over 400 applications) on Intrepid.

To address the performance challenge under congestion, some recent research efforts has been taken. CALCioM [4] focuses on reducing the interference between multiple applications that run concurrently in HPC system to decrease the contention on I/O network. In [2], [5], Gainaru and Aupy studied the problem: how to schedule the I/O requests to improve the I/O performance under bandwidth congestion. But they all haven't taken account into effect of memory hierarchy on reducing I/O congestion. In [3], an online read algorithm has been proposed, which mitigates the contention on SSDs by scheduling some I/O requests on parallel file system (PFS). But this method just considers one kind of resource congestion.

Although the above mentioned methods improve the I/O performance in some extent, they lack of a global consideration by utilizing memory hierarchy. In order to conduct a comprehensive analysis, we explore I/O scheduling under the contentions both on SSDs and I/O bandwidth. In this work, we first analyze the effects of I/O congestion between

![](_page_0_Picture_14.png)

69

different applications on I/O network and contention between different processes on SSDs. Secondly, a memory hierarchy aware I/O scheduling method is proposed to detect contentions and schedule I/O requests. The contributions of this paper are as follows: (1) We propose a memory hierarchy aware I/O scheduling to relieve the contention issue on SSDs and I/O network. This online algorithm could detect possible contention and utilize memory hierarchy resource to relieve this situation. (2) We give the theoretical analysis and extensive experiments to prove the effectiveness of our method.

The rest of this paper is organized as follows. The related work has been discussed in Section II. We introduce the system model and the scheduling problem in Section III. The memory hierarchy aware I/O scheduling method has been proposed in Section IV. In Section V, the theoretical analysis and extensive experiments has been shown. In Section VI, we provide the conclusion and give our future research directions.

## II. RELATED WORKS

The related literature about this work has been carefully reviewed in two areas: I/O scheduling and hybrid storage system. I/O scheduling techniques rearrange the order of I/O requests to improve the system performance, such as I/O throughput, system utilization. The researches about hybrid storage system are about how to introduce SSDs to the storage system to relieve the I/O bottleneck.

## *A. I/O scheduling in HPC*

In the field of high performance computing, I/O scheduling has been widely studied by many researchers to pursue the full use of I/O system. Parallel I/O [6] can improve the I/O performance of single application through multi-process parallel accessing data. Parallel I/O scheduling further improve the performance to meet the current demand of many data-intensive applications. Disk-directed I/O [7] widens the bandwidth of disks, and server-directed I/O [8] improves the utilization of network server. There are some further works to optimize the collective I/O [9], which implement an I/O scheduling to coalescing non-contiguous requests into a large contiguous request. In [10], the increasing shuffle cost has been considered to improve collective I/O.

The above mentioned approaches have been introduced just for single application or in the row level where the high level characteristics can't be used. In current environment, many applications have been executed concurrently with a competitive manner. In [11], [12], the authors point out I/O congestion as a main problem for next generation scale platforms. Applicationside I/O scheduling [13], [14] can handle the problem of performance variability due to the share of resources. In some other work [15], [16], machine learning has been used into I/O scheduling to automatically tune the performance. For special platform, Jaguar supercomputer, in [17], its I/O behaviors and performance variability has been studied. In order to avoid congestion, [2], [4] analyze the benefits of interrupting or delaying.

# *B. SSDs based hybrid storage*

The other related work is hybrid storage systems, which introduce SSDs to memory hierarchy to improve storage system performance. A comprehensive survey has been proposed in [18], which explores different architectures and corresponding algorithms. NVMalloc [19] provides a simple programming API to simplify the use of SSDs in HPC systems. CARL [20] proposes cost model based method to place data in different devices. iTransformer [21] uses SSDs as a buffer to extend HDDs scheduling queue to optimize performance.

The researches closest to our study are [2], [3]. The authors investigate the problem of performance optimization under contention in HPC. Our study is motivated by them, but much more general. The congestion we considered isn't on single resource, which maybe happened on SSDs or I/O network. The idea of utilizing memory hierarchy has been further applied to optimize the system performance.

## III. PLATFORM MODEL AND MOTIVATION

In this section, we describe a general abstract platform model and provide the motivation. We target a parallel platform with hybrid storage system, which use SSDs as caches. When multiple scientific applications run on such system, the contention on parts of storage system maybe cause performance degraded dramatically.

# *A. Platform Model*

A common parallel platform consists of computing network, I/O network and storage system as shown in Fig. 2. Computing network usually composes of a plenty of identical compute nodes, which maybe have multiple cores. Among compute nodes, the communications is provided by high speed links. I/O network, which is constructed by Ethernet or InfiniBand, links the computing network with storage system. Storage system is made up of HDDs arrays and storage services are provided by parallel file system like Luster, GPFS.

![](_page_1_Figure_14.png)

Fig. 2. Abstract parallel platform model

There are many applications concurrently running on such system and each of them was executed on many independent and dedicated compute nodes. Each compute node has a private SSD as burst buffer or cache, which is common in current field of HPC. The computational task assigned to each compute node can be divided into many subtasks. Each subtask can be assigned to a process. The more the number of processes on each compute node, the short the complete time of overall application due to the higher parallelism. Fig. 3. illustrates the process of application execution simply.

![](_page_2_Figure_1.png)

Fig. 3. The process of application execution

# *B. Motivation*

Under congestion, system performance can be influenced dramatically due to application interference. There are many related works that discussed this phenomenon. The read contention on SSDs could causes up to 50% performance degrades via real testing in [3]. The congestion on I/O network can cause up to a 70% decrease in I/O efficiency of applications in some cases according to [2]. In our work, we comprehensively consider both contentions due to the relationship of their effects on performance. The techniques to relieve the contention on SSDs may increase the burden of I/O network. Therefore, there exists a tradeoff between SSDs and I/O network.

When I/O requests are scheduled between different levels of memory hierarchy, the characteristics of different storage devices can be utilized efficiently. The contention on these resources will be mitigated through the memory hierarchy aware I/O scheduling, and then system performance will be increased.

# IV. METHOD

In this section, we describe the method in detail that schedules I/O requests among memory hierarchy. The memory hierarchy aware I/O scheduling method can detect and relieve the contention on SSDs and I/O network on the fly.

## *A. Formalization*

In our target platform, each compute node has equipped with an I/O card of bandwidth b, and the speed to access SSD is Sssd. The I/O network and parallel file system can provide with a total bandwidth B. The number of compute nodes is

N. We assume that K applications will be executed concurrently on the abovementioned platform, each of them consists of nk tot instances can be assigned to βk dedicated compute nodes. Each instance need to transfer a volume volk,i io of data to or from the I/O system. Let r be the actual I/O rate by each compute node of the k-th application. Therefore, for the simplest case without congestion, the time to perform the I/O transfers for the the i-th instance of the k-th application is as Eq. (1).

$$T_{i o}^{k,i}=\frac{vol_{i o}^{k,i}}{\operatorname*{min}(\beta^{k}r,\,B)}\qquad\qquad(1)$$

When many applications access to I/O system simultaneously, the total I/O bandwidth will be shared among all applications and then the congestion will likely occur. The original scheduler should be assign a access rate to each application, namely rk. However, the congestion can cause the performance degrade obviously, so the original system scheduling might be non-efficient and the contention avoided method should be proposed.

#### *B. Online algorithm for contention detection*

Because scientific computing involves enormous amount of data to analysis, I/O become gradually a scarce resources. The contention on these resources is owed to too large total access size and the number of requests. To mitigate the effect of contention, we first propose an online algorithm to detect it, which run on each compute node. The algorithm is built from an experiments based coarse model, which come from two observations. First, too much I/O requests could cause performance degradation due to resource contention. Second, contention is caused when both the number of requests and total access size over certain thresholds.

In this work, contention includes two kinds: SSDs, I/O network. Although the detection technique is similar, the particular parameters are different. Therefore, we provide two algorithms to describe them. The detection algorithm on SSDs is provided in Alg. 1 and on I/O network in Alg. 2.

| Algorithm 1 Detect contention on SSDs |
| --- |
| Input: Nnode−proc, Sproc−iosize |
| Output: flag |
| 1: function DETECTSSD(Nnode−proc, Sproc−iosize) 2: |
| if Nnode−proc×Sproc−iosize > α and Nnode−proc > β |
| then |
| 3: flag = Ture |
| 4: else |
| 5: flag = Flase |
| 6: end if |
| 7: return flag |
| 8: end function |

Function DETECTSSD have two parameters:Nnode−proc, Sproc−iosize. Nnode−proc denotes the number of processes in the compute node, and Sproc−iosize denotes the average I/O size for each process. α is the maximal I/O size to access SSDs, which can't cause contention. β is the maximal number of processes on each compute node, which is allowed for optimal performance. These environmental variables are system specific, and their values dependent on different specific system. In order to discover the actual values, the experiment based procedure is gradually increasing I/O size and number of processes until the turning point appears.

The method to detect the congestion on I/O network is similar to Function DETECTSSD. It isn't running in each compute node but an dedicated scheduling node because of the need of overall environmental information. When the number of I/O requests and the total I/O size to PFS exceed some thresholds, the contention likely occurs. Like Function DETECTSSD, we use A representing the maximal I/O size to access SSDs, and B representing the maximal number of total processes in the system. The actual number of total processes can be calculated in Eq. 2 and the actual I/O size is provided in Eq. 3. The detail algorithm has been shown in Alg. 2.

$$N_{total-proc}=\sum_{i=1}^{K\times\beta^{k}}N_{node-proc}\tag{2}$$

$$S_{total-iosize}=N_{total-proc}\times S_{proc-iosize}\tag{3}$$

```
Algorithm 2 Detect contention on I/O
Input: Ntotal−proc, Stotal−iosize
Output: flag
 1: function DETECTIO(Ntotal−proc, Stotal−iosize)
 2: if Stotal−iosize > A and Ntotal−proc > B then
 3: flag = Ture
 4: else
 5: flag = Flase
 6: end if
 7: return flag
 8: end function
```
# *C. Memory hierarchy aware I/O scheduling method*

While the contention occurs, we should provide some strategies to relieve this situation. In this work, we transfer the data access among memory hierarchy. First, we detect if the contention happened on SSDs. If true, we transfer some data access to PFS. Second, we detect if contention appear on I/O network. If true, we should delay the execution of that process. The process of the detail scheduling shows in Alg. 3.

#### V. RESULTS

In this section, we present the experiments of our proposed memory hierarchy aware I/O scheduling method. We compare it with the single contention methods [2], [3]. The experimental results show our general method can obviously improve the system performance.

# Algorithm 3 schedule I/O requests

| Input: total processes, read size |  |
| --- | --- |
| Output: directions for each process to do I/O |  |
| 1: procedure | SCHEDULEIO |
| 2: while Ture do |  |
| 3: | if DETECTSSD( ) then |
| 4: | if DETECTIO( )==False then |
| 5: | tranfer some processes to access PFS. |
| 6: else |  |
| 7: | delay some processes |
| 8: | end if |
| else 9: |  |
| 10: | access data from SSDs |
| end if 11: |  |
| end while 12: |  |
| 13: end procedure |  |

#### *A. Experimental setup*

All experiments were performed on a 65-node Linux-based cluster test bed. This cluster is composed of one Sun Fire X4240 head node, with dual 2.7 GHz Opteron quad-core processors and 8GB memory, and 64 Sun Fire X2200 compute nodes with dual 2.3GHz Opteron quadcore processors and 8GB memory. Each node is equipped with one solid-state drive, and Ubuntu 4.3.3–5 system with kernel 2.6.28.10. All 65 nodes are connected with Gigabit Ethernet.

To demonstrate our method could process really big data and applicable to various real scientific datasets, two real world simulations' aggregated 2TB binary double-precision 3D datasets are used for evaluation: 1). S3D [22]. A first principles-based direct numerical simulation of reacting flows that aids the modeling and design of combustion devices. 2). FLASH [23]. A parallel hydrodynamics code developed to simulate astrophysical thermonuclear flashes in two or three dimensions, such as Type Ia supernovae, Type I X-ray bursts, and classical novae. The datasets are striped across 30 Object Storage Targets(OSTs) on the PFS and striping size is 1MB.

# *B. Performance evaluation*

In this section, we first demonstrate the effectiveness of memory hierarchy aware I/O scheduling method. The system specific parameters have been estimated through experimental testing. α is 6000MB. β is 16 processes per node. A is 500GB. B is 4096 processes.

TABLE I THE EXPERIMENT RESULTS

|  | SSD contention [3] | I/O congestion [2] | Our method |
| --- | --- | --- | --- |
| S3D | 15.6 | 18.5 | 13.1 |
| FLASH | 17.8 | 23 | 15.2 |

Tab. 1 gives the results. For both simulations, our method can obtain the best execution time. The improvement comes up to 20% than other two methods. Possible reasons for our results might come from the tradeoff between SSD and PFS.

# VI. CONCLUSION AND FUTURE WORK

With the scale of scientific computing application became bigger and bigger, the lack of I/O resources, like SSDs and I/O, bandwidth cause serious contention on these resources among applications. In order to improve the performance of parallel application and the utilization of HPC system under contention, I/O scheduling reorder the I/O requests using the characteristics of applications and system to explore the potential of performance improvement.

In this work, we first design an online detection algorithm to detect the existence of resource congestion using the environment variables and the global I/O requirements of applications. When the contentions become harmful to the performance, the memory hierarchy aware I/O scheduling we proposed will give an appropriate schedule on the I/O requests that will be transferred in memory hierarchy. Finally, the theoretical analysis and experiment results show our method can efficiently improve the performance. The use of global system information can obviously optimize the I/O scheduling, and then the optimized scheduling schedules the I/O requests among memory hierarchies to increase system utilization and further to reduce the execution time of applications.

Instead of SSDs cache-based method, hybrid storage system in HPC field can be constructed by SSDs tiering method [18]. In this work, we just explore memory hierarchy aware I/O scheduling on HPC system that uses SSDs as burst buffer or cache. Since the tiering based storage system has some advantage and has different data management manner, we expect the memory hierarchy aware I/O scheduling on this kind of system to be useful. Future work will devoted to apply the method purposed in this paper to SSDs tiering based HPC system, which may be difficult for the more complex data management manner.

#### ACKNOWLEDGMENT

This study was supported by the National Key Research and Development Plan's Key Special Program on High performance computing of China, No. 2017YFB0203201.

# REFERENCES

- [1] J. He, J. Bennett, and A. Snavely, "Dash-io: an empirical study of flashbased io for hpc," in Proceedings of the 2010 TeraGrid Conference. ACM, 2010, p. 10.
- [2] A. Gainaru, G. Aupy, A. Benoit, F. Cappello, Y. Robert, and M. Snir, "Scheduling the I/O of HPC Applications Under Congestion," in 2015 IEEE International Parallel and Distributed Processing Symposium, 2015, pp. 1013–1022.
- [3] W. Zhang et al., "Exploring Memory Hierarchy to Improve Scientific Data Read Performance," in 2015 IEEE International Conference on Cluster Computing, 2015, pp. 66–69.
- [4] M. Dorier, G. Antoniu, R. Ross, D. Kimpe, and S. Ibrahim, "CALCioM: Mitigating I/O Interference in HPC Systems through Cross-Application Coordination," in 2014 IEEE 28th International Parallel and Distributed Processing Symposium, 2014, pp. 155–164.
- [5] G. Aupy, A. Gainaru, and V. L. Fèvre, " I/O Scheduling for Super-Computers," in High Performance Computing Systems. Performance Modeling, Benchmarking, and Simulation, 2017, pp. 44–66.
- [6] F. Z. Boito, E. C. Inacio, J. L. Bez, P. O. A. Navaux, M. A. R. Dantas, and Y. Denneulin, "A Checkpoint of Research on I/O for High-Performance Computing," ACM Comput. Surv., vol. 51, no. 2, pp. 23:1–23:35, Mar. 2018.

- [7] D. Kotz. Disk-directed I/O for MIMD multiprocessors. Technical Report PCS-TR94-226, Dartmouth College, July 1994.
- [8] K. E. Seamons, Y. Chen, P. Jones, J. Jozwiak, and M. Winslett. Serverdirected collective I/O collective I/O in Panda. In Proceedings of SC '95, San Diego, CA, Dec. 1995.
- [9] R. Thakur, W. Gropp, and E. Lusk. Data sieving and collective I/O in ROMIO. In Proc. of the 7th Symposium on the Frontiers of Massively Parallel Computation, pages 182–189. IEEE, Feb. 1999.
- [10] J. Liu, Y. Zhuang, and Y. Chen, " Hierarchical Collective I/O Scheduling for High-Performance Computing," Big Data Research, vol. 2, no. 3, pp. 117–126, Sep. 2015.
- [11] R. Biswas, M. Aftosmis, C. Kiris, and B.-W. Shen, "Petascale computing: Impact on future NASA missions," Petascale Computing: Architectures and Algorithms, pp. 29–46, 2007.
- [12] J. Lofstead and R. Ross, "Insights for exascale IO APIs from building a petascale IO API," in Proceedings of SC13. ACM, 2013, p. 87.
- [13] X. Zhang, K. Davis, and S. Jiang, "Opportunistic data-driven execution of parallel programs for efficient I/O services," in Proceedings of IPDPS12. IEEE, 2012, pp. 330–341.
- [14] J. Lofstead, F. Zheng, Q. Liu, S. Klasky, R. Oldfield, T. Kordenbrock, K. Schwan, and M. Wolf, "Managing variability in the IO performance of petascale storage systems," in Proceedings of SC10. IEEE Computer Society, 2010.
- [15] B. Behzad, L. H. V. Thanh, J. Huchette, S. Byna, R. A. Prabhat, Q. Koziol, and M. Snir, "Taming parallel I/O complexity with auto-tuning," in Proceedings of SC13, 2013.
- [16] S. Kumar et al., "Characterization and modeling of pidx parallel I/O for performance optimization," in Proceedings of SC13. ACM, 2013.
- [17] B. Xie, J. Chase, D. Dillow, O. Drokin, S. Klasky, S. Oral, and N. Podhorszki, "Characterizing output bottlenecks in a supercomputer," Proceedings of SC12, pp. 1–11, 2012.
- [18] J. Niu, J. Xu, and L. Xie, "Hybrid Storage Systems: A Survey of Architectures and Algorithms," IEEE Access, vol. 6, pp. 13385–13406, 2018.
- [19] C. Wang, S. S. Vazhkudai, X. Ma, F. Meng, Y. Kim, and C. Engelmann, "Nvmalloc: Exposing an aggregate ssd store as a memory partition in extreme-scale machines," in IPDPS, 2012 IEEE 26th International. IEEE, 2012, pp. 957–968.
- [20] S. He, X.-H. Sun, B. Feng, X. Huang, and K. Feng, "A cost-aware region-level data placement scheme for hybrid parallel i/o systems," in CLUSTER, 2013 IEEE International Conference on. IEEE, 2013, pp. 1–8.
- [21] X. Zhang, K. Davis, and S. Jiang, "itransformer: Using ssd to improve disk scheduling for high-performance i/o," in IPDPS, 2012 IEEE 26th International. IEEE, 2012, pp. 715–726.
- [22] J. H. , A. Choudhary, B. De Supinski, M. DeVries, E. Hawkes, S. Klasky, W. Liao, K. Ma, J. Mellor-Crummey, N. Podhorszki et al., "Terascale direct numerical simulations of turbulent combustion using s3d," Computational Science & Discovery, vol. 2, no. 1, p. 015001, 2009.
- [23] B. , K. Olson, P. Ricker, F. X. Timmes, M. Zingale, D. Q. Lamb, P. MacNeice, R. Rosner, J. W. Truran, and H. Tufo, "FLASH: An adaptive mesh hydrodynamics code for modeling astrophysical thermonuclear flashes," The Astrophysical Journal Supplement Series, vol. 131, pp. 273– 334, Nov. 2000.

