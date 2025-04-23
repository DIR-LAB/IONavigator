# **A Dynamic Replication Mechanism to Reduce Response-Time of I/O Operations in High Performance Computing Clusters**

Ehsan Mousavi Khaneghah, Seyedeh Leili Mirtaheri, Lucio Grandinetti Center of High Performance Computing for Parallel and Distributed Processing, University of Calabria Rende, Italy {emousavi, mirtaheri, lucio}@unical.it

*Abstract*— **Extraordinary large datasets of high performance computing applications require improvement in existing storage and retrieval mechanisms. Moreover, enlargement of the gap between data processing and I/O operations' throughput will bound the system performance to storage and retrieval operations and remarkably reduce the overall performance of high performance computing clusters. File replication is a way to improve the performance of I/O operations and increase network utilization by storing several copies of every file. Furthermore, this will lead to a more reliable and faulttolerant storage cluster. In order to improve the response time of I/O operations, we have proposed a mechanism that estimates the required number of replicas for each file based on its popularity. Besides that, the remaining space of storage cluster is considered in the evaluation of replication factors and the number of replicas is adapted to the storage state. We have implemented the proposed mechanism using HDFS and evaluated it using MapReduce framework. Evaluation results prove its capability to improve the response time of read operations and increase network utilization. Consequently, this mechanism reduces the overall response time of read operations by considering files' popularity in replication process and adapts the replication factor to the cluster state.** 

*Keywords- File Systems; File Replication; Adaptive Storage; Dynamic Replication* 

## I. INTRODUCTION

Search engines, genetic simulation programs, and seismography tools are examples of computational applications that require high performance storage and retrieval mechanisms to process large datasets. As a result, various storage and retrieval mechanisms have been introduced in order to improve different aspects of system performance such as reliability and extendibility [1].

Data replication is a well-known mechanism to overcome limitations of computational environments and achieve higher I/O performance [2]. Illustrating that, Grid and Cloud computing are among many distributed computing environments experiencing shortage of network and storage bandwidth which can be avoided by efficient data replication [3]. Moreover, it will lead to more reliable and extensible storage systems, increase system fault tolerance against failures, and improve network utilization [4]. It can also avoid data transmission bottlenecks by reducing the response time of I/O operations. Increasing the number of replicas can improve the overall I/O performance by using storage capacity and network bandwidth of several nodes instead on relying on a single computational node [5].

In order to improve the I/O operations response time in high performance computing clusters, we have proposed a dynamic mechanism that estimates the replication factor of each file based on its popularity and cluster's storage state. Therefore, this mechanism considers some aspects of the execution state of storage cluster in determining the appropriate number of replicas for each file.

A brief introduction about proposed replication mechanisms in the field of high performance computing is presented in section II. Elaboration on our proposed mechanism and evaluation results are

Amir Saman Memaripour, Mohsen Sharifi School of Computer Engineering Iran University of Science and Technology Tehran, Iran {memaripour, msharifi}@iust.ac.ir

discussed in sections III and IV respectively. Finally, some concluding remarks and future works are presented in section V.

#### II. RELATED WORKS

In the field of data storage and retrieval, replication is performed to improve different aspects of system performance such as reliability, response time, power consumption and network traffic [6] [7] [8] [9]. Because of the variety of application domains, various replication methods have been proposed to address different characteristics of system performance. As a rule of thumb, replication mechanisms can be classified into dynamic and static methods [10]. Static methods do not consider file status, e.g., the number of readers and writers of each file, and perform in a predefined manner. As a result, some files may experience shortage of replicas while others exceed their required number of replicas.

On the other hand, dynamic methods estimate the required number of replicas for each file based on its status [10]. In order to reduce the access latency, data blocks can be replicated across the hard disk according to their access pattern which is an example of dynamic replication methods [8]. As a matter of fact, proposed dynamic replication mechanisms can be classified into local and global methods. In high performance storage clusters and computing environments, local methods are not able to satisfy performance requirements and global replication methods must be used to fulfill these demands [11].

An adaptive replication mechanism has been proposed in [12] which uses AI methods to estimate file replication factor. This mechanism performs replication in two phases and considers handful parameters such as read and write frequencies and internode communication costs in this way. In the first step, replication is performed once the variations of read and write frequencies reduce to a predefined threshold. After that, the number of replicas of each file will be increased or decreased based on the changes of its access pattern. Despite the performed optimizations to reduce the computational overhead, this mechanism is not an appropriate candidate for high performance computing environments due to its high processing requirements and expensive initialization phase. In addition, replication factor updates are restricted to the changes of read and write frequencies and execution state of the storage cluster is not considered in this manner [12].

Another replication mechanism has been proposed in [6] that considers system file missing rate and system bytes missing rate in order to improve system reliability. One of the most important features of this mechanism is the consideration of remaining storage space in calculating file replication factors. The greedy replication algorithm of this mechanism performs replication to achieve higher reliability levels and does not make any assumptions about improving I/O response time.

Replicating files based on their access frequency is another approach which is followed in [13]. This mechanism is similar to replication strategies of peer to peer systems that behave in the same way towards various access types, e.g., read and write [14]. In order to keep the storage system balanced, an impact factor is assigned to each file access based on the access history of the respective file. Access time is the most important parameter in calculation of these factors and a more recent file access achieves higher impact factor than previous ones. Consequently, a weightedaverage on corresponding impact factors is performed to estimate the replication factor of each file. This mechanism has to maintain historical information about file access patterns in order to estimate replication factors which reduces system extendibility and is considered as a weakness point.

By extending the number of considered parameters effecting files replication factor, [15] provides a better adaptation to files access pattern than previous works. This mechanism continuously stores changes of several parameters including timestamp, path, access type, I/O size, elapsed time of every access, and destination hostname in a database which is used to estimate the proper replication factor for each file. Furthermore, it selects hosts to store new replicas based on their future estimated throughput in order to guarantee that most of the I/O operations will perform in a defined time. Just like the one in [13], this mechanism requires access history of files. Moreover, it does not consider access locality in replica distribution.

Preserving the consistency of replicas is another important issue in file replication. ORCS and DMS, that are proposed in [16] and keeps all replicas of a file consistent once its contents change, are among various mechanisms introduced to preserve replicas consistency. DMS is proposed to adapt data location to user requests and reduce the distance between reader nodes and data replicas. In addition, ORCS and DMS consider available storage space of each host in estimating replication factor. In order to gather required information, they use monitoring tools like NWS and Ganglia and store this information in a database. As one of its main advantages, this mechanism takes into account the access locality in file replication.

Our proposed mechanism is designed to improve response time of read operations without storing any historical data about files access patterns. Moreover, it requires less computational power compared with other replication mechanisms that use AI methods or access profiling. As a result of limiting allowed file operations to read, write and delete, replica consistency issues are not considered in the design of this mechanism.

## III. PROPOSED MECHANISM

In order to design the proposed mechanism, we have considered several facts and assumptions about high performance computing clusters. Some of them are mainly due to the nature of high performance computing environments while the others relate to HDFS which is used as the implementation platform [17]. Our considered assumptions are as follows:

- - Every file is stored as a series of data blocks with a predefined size.
- - Read, write, and delete are the only allowed I/O operations on every data block.
- - It is not possible to change the contents of any data block after its creation. Moreover, only one user can write on a data block at a time.
- - Data blocks are usually shared among several computational nodes in a storage cluster.

Assuming the above points, which are the basic design considerations of HDFS, we can leave the data consistency issues behind and focus on the main problem. Furthermore, existing locking and access control mechanisms of HDFS can take care of data blocks consistency issues and provide the proposed mechanism with a consistent replication facility. The following list contains the considered facts in design of the proposed mechanism:

- - Any computational node is running many tasks simultaneously at any given time.
- - We have a limited storage capacity in any storage cluster that should be fairly shared among all stored files.
- - Because of the great number of data blocks in a storage cluster, storing access history of these blocks is not feasible. Moreover, if these access histories are being stored, lots of processing power should be dedicated to management and maintenance of this information.

Considering the above items, it can be inferred that behavior of the proposed mechanism must be adapted to the current state of storage cluster. This adaptation is performed by changing the number of replicas of each file based on the remaining storage space of cluster. Besides that, shared access to network bandwidth and storage media should be considered in order to avoid performance downgrade due to resource overload.

With regards to these considerations, we have proposed a mechanism to estimate the number of replicas for each file based on its popularity and the remaining storage space of cluster. Next, the architecture of this mechanism is discussed. After that, its behavior is introduced in more detail.

## A. *Architecture*

In this mechanism, two agents are responsible for estimating replication factor and performing file replication. RFEA estimates the required number of replicas for each file and RFSA adapts this number to the remaining storage space of cluster. These agents use the APIs provided by HDFS to change replication factors and monitor files access pattern and cluster storage state. For example, *setReplication* and *getReplication* are used to get the current replication factor of a file and change it [18]. Modular design of this mechanism and the interconnections between RFEA and RFSA are illustrated in Fig. 1.

RFEA and RFSA are implemented as a multi-thread program which runs on the NameNode in a Hadoop cluster. As the HDFS provided APIs could be executed remotely, it is possible to run this program on every node of the cluster. However, we have decided to run and evaluate this mechanism on the NameNode to reduce its communication cost. The next sections discuss RFEA and RFSA agents in more details and demonstrate how they estimate replication factor and adapt it to the remaining storage space.

## B. *Replication Factor Estimation Agent*

By measuring the available network bandwidth of reader nodes, RFEA estimates the replication factor of every file. As a result of increasing the replication factor, reader nodes can utilize the available bandwidth and the performance of I/O operations will be improved. Based on the mentioned assumptions, no changes can be made on the contents of a data block once it is written to the filesystem and append operation is not supported here. Consequently, the relation between number of replicas and the cost of changing a data block's contents is not considered.

TABLE I. DEFINITON OF A NUMBER OF SETS USED BY RFEA TO ESTIMATE THE REPLICATION FACTOR

|  | = | { ∀ | ∈ |  | ∶ |  ℎ  ! "#  } |  |  |  | ∈ | $% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| & | & | = |  |  |  | '*$#,# ,#-" . "/,$" "!%$0 .  |  |  |  |  |  |
|  |  | = {∀ |  |  |  | ∈  ∶  ℎ  "!%$0 . } |  |  | ∈ $% |  |  |
| & | & | = |  |  | ,""  ,#-" . "!%$0 .  |  |  |  |  |  |  |
|   |  | = {∀ |  | ∈  |  | ∶ !() > $2!()} |  |  |  |  |  |
|  | = | {∀ | ∈ |  ∶ |  | 4$%() ≥ } |  $  .$  0   |  |  |  |  |

A number of sets that RFEA uses to estimate the number of replicas are listed in Table I. AS and HS contain sets of data nodes reading and hosting a data block of Fi respectively. The set of crowded data nodes is assigned to CN and indicates a number of data nodes without notable available network bandwidth to make use of new replicas. Assigning a value to tn depends on the hardware configuration and computational environment characteristics. However, we have considered tn = 0.9 to facilitate the evaluation of proposed mechanism. On the other hand, there are several data nodes capable of utilizing their available network bandwidth and improving the performance of read operations. These nodes, defined as NDN, are provided with higher network throughput compared to their disk read throughput and increasing the number of replicas will probably improve the response time of their I/O operations.

First, we make a set of data nodes with remote access to data blocks of a file in order to estimate its proper replication factor. It is possible to make this set by monitoring the activities of data nodes, but it is not a feasible idea in large storage clusters due to its communication and computational costs. Therefore, we have used (1) in this manner. 3

$$R3S_{F_{i}}=A S_{F_{i}}-(H S_{F_{i}}-N D N)\qquad\qquad(1)$$

By eliminating the data nodes belonging to CN, remaining nodes of R3S will be capable of utilizing new replicas. These nodes are determined using (2) and called potentially starving nodes. In case we increase the number of replicas by half the size of PSN, the potentially starving nodes can utilize their available network bandwidth to read data from the newly created replicas and improve their read performance accordingly. In fact, this idea stems from two basic assumptions. First, we assumed that the replica host selection algorithm will find an appropriate host to store the new replicas. Besides that, replicating a data block will reduce the access load on at least one of its other replicas.

$\rm{PSN}_{F_{1}}=\rm{R3S}_{F_{1}}-\rm{CN}$ (2)

For this reason, the current replication factor of Fi should be increased by half the size of PSN. In order to prevent momentary changes of access patterns from affecting our calculations, a weighted-average is performed, as illustrated in (3), to estimate the required number of replicas. Here, we have assumed α = 0.5. The outcome of this equation reflects the required number of replicas for Fi.

 (
) = ×  (
−1) + (1 − ) × (3)

As a means to adapt the replication factor of each file to the remaining storage space of cluster, RFSA provides RFEA with a feasibility factor, FF in [0, 1], which is used to determine the final replication factor of every file. The next section discusses how this factor is calculated in detail.

$${\rm FRF}_{i}(n)={\rm FF}_{i}\times{\rm RF}_{i}(n)\tag{4}$$

After the proper replication factor of Fi is estimated using (4), required changes will be made based on the current replication factor and the calculation results. If the current replication factor of Fi is less than *FRF(n)*, creation of new replicas will be scheduled. Otherwise, redundant replicas of Fi will be deleted.

 

## C. *Replication Factor Supervision Agent*

Due to the finite storage space of clusters, a limited number of replicas could be stored for every file. In case there is enough free space, replication can be performed on every file till it reaches its proper replication factor. However, the number of replicas should be adapted to the available storage space of cluster as the remaining storage space falls below a defined threshold. Thus, a parameter called FF is defined for every file that indicates the achievable portion of its required replicas. In order to adapt the replication process to the remaining storage capacity of cluster, RFSA calculates the value of FF for each file and provides RFEA

![](_page_2_Figure_14.png)

Figure 1. Modular design of the proposed mechanism.

**procedure** AdapT‒

 

**input:** *Max-Heap* over  of files with & & > *MinRepFactor* **while** *OverallStorageUsage* is not in *GreenArea* do

$F_{t}=$ removeRoot(_Max-Heap_)

**if** ($F_{t}$ _is null_) **break** _// Max-Heap is empty_

$FF_{F_{t}}=(|HS_{F_{t}}|-1)$ _/ $FF_{F_{t}}$ (n)_

setReplication($F_{t}$, $|HS_{F_{t}}|-1)$

**value** $|-1$ _is F = $F$ _is half-life_ $F_{t}$

if ($\left|HS_{F_{i}}\right|>$_MinRepFactor_) addNode(_Max-Heap_, $F_{i}$)

Figure 3. The pseudo codes of AdapT+ and AdapT‒ procedures.

with it. Indeed, its value will be increased or decreased with regards to the available storage space. The proper value for FF is determined by AdapT, a programming thread created by RFSA at special circumstances. Fig. 2 shows how AdapT reacts to the changes of cluster storage space.

In facing with the changes of cluster storage state, AdapT should detect the over-replicated files and adapt their replication factor to the new situation. In this way, it can perform the selection in a conscious manner or randomly. In the latter approach, AdapT will select an arbitrary file and changes its replication factor with regards to the remaining storage space. On the other hand, first approach considers FF in selecting candidate files for adaptation. The conscious selection approach acquires higher accuracy in selecting proper files for adaptation compared with the random selection approach. Although it requires more memory space than the random approach, AdapT employs this approach due to its high accuracy level. Fig. 3 contains the pseudo code of AdapT in the form of two procedures, AdapT+ and AdapT‒.

The roadmap of AdapT will be designed based on a parameter provided by RFSA. In case the number of replicas should be increased, AdapT+ will be executed. Otherwise, AdapT‒ will be called to reduce the replication factor of candidate files. The pseudo codes of these two procedures are described in Fig. 3. In order to reduce the processing overhead of candidate selection, AdapT is provided with two heap data structures: a max-heap and a min-heap to select the files with the maximum number of FF and the minimum number of FF respectively [19]. RFSA is responsible

#### **procedure** AdapT+

**input:** *Min-Heap* over  of files with  < 1.0 **while** *OveralStorageUsage* is in *GreenArea* do

$F_{i}=$ removeRoot(_Min-Heap_)

if ($F_{i}$ is _null_) break // Min-Heap is empty

$FF_{i}=(|HS_{F_{i}}|+1)$ / $FF_{F_{i}}$ ($n$)

setRelation($F_{i}$, $|HS_{F_{i}}|+1$)

if ($FF_{F_{i}}<1.0$) addNode(_Min-Heap_, $F_{i}$)

for updating these structures and performs this operation with regards to files replication statistics. Consequently, RFSA will provide RFEA with FF and adapt the number of replicas of each file to the remaining storage space of cluster using a programing thread called AdapT.

#### IV. EVALUATION

Considering the assumptions mentioned in section III, we have measured the proposed mechanism in terms of response time and read operations performance. Once a file becomes under-replicated or a new data block is going to be written, HDFS constructs a pipeline to perform replication in a distributed manner. As a result, the more number of replicas leads to less replication time in case of replicating existing data blocks. Moreover, the contents of data blocks are immutable and do not change after its creation. Therefore, we have not evaluated how the proposed mechanism might affect the performance of write operations in a storage cluster.

In order to perform the evaluation, a MapReduce job has been employed which calculates the average temperature and maximum temperature of every year [20]. This job is provided with an input file with the size of 10.13 GB containing NCDC climate data of the years 1937 to 2009. This job breaks down to 162 map tasks and a reduce task running on a Hadoop cluster. We have evaluated the execution time and I/O performance of this job in the presence of our proposed mechanism and a static replication mechanism, when the replication factor is equal to 3, and in the absence of any replication mechanism.

![](_page_3_Figure_15.png)

Figure 2. The effect of overall remaining storage space on AdapT execution.

741

![](_page_4_Figure_0.png)

Figure 5. The effect of replication mechanism and number of simultanous jobs on the read performance.

Our test cluster comprises 8 computational nodes running Apache Hadoop version 1.0.1 [21]. Every node is provided with 4 gigabytes of RAM, 250 gigabytes of disk drive, and one Atheros Gigabit network adapter and runs Ubuntu 11.04 on an AMD Phenom Quad Core 3.2 GHz or an Intel Core 2 Quad 2.4 GHz. Two of these eight nodes are assigned to the NameNode and JobTracker and the rest are tagged as DataNodes.

In the first test, we have evaluated the average execution time of the MapReduce job using three different replication policies. The results of executing the job in the presence of the proposed mechanism, a static replication method and no replication are presented in Fig. 4. For static replication, a replication factor of 3 is assigned to every file. Based on the experimental results, our mechanism can extremely reduce the response time of read operations for I/O-bound applications.

Fig. 5 demonstrates the experimental results of the second test which measures the average read performance of the MapReduce job while several jobs are simultaneously performing I/O operations on the same file. Note that same replication factor policies as the previous test have been used here. Besides that, the horizontal bar in the figure represents the number of simultaneously running jobs. Considering the results, our proposed mechanism always provides more read performance than the other two replication methods. Furthermore, the only parameters reducing the performance of this mechanism are resource limitations and HDFS replication policies that prevent it from increasing the replication factor according to files' popularity.

Summarizing the results, our proposed mechanism can improve the read performance of applications with long-term I/O operations without requiring additional communications.

## V. CONCLUSION AND FUTURE WORKS

In storage clusters, data replication is performed to improve various aspects of system performance such as response time and reliability. Our proposed mechanism estimates the proper number of replicas for each file based on files' popularity and the overall remaining storage space in order to reduce the response time of read operations in HPC clusters. Using Hadoop as the implementation platform, several assumptions have been considered in designing the proposed mechanism along with general facts of high performance computing environments. These facts and assumptions are listed in section III.

![](_page_4_Figure_9.png)

Figure 4. Average execution time of the MapReduce job.

For every file in the storage cluster, the proposed mechanism provides a set of data nodes hosting one or more of its data blocks. In case the replication mechanism considers these sets in selecting data nodes to host the newly created replicas, the performance of I/O operations in terms of response time, network traffic, and replication cost will be improved. For instance, the data node with the least aggregate network distance to reader nodes is a good candidate to reduce the overall network traffic and improve data replication speed. Consequently, data structures provided by the proposed mechanism can be helpful in dynamic replica host selection besides their basic application in replication factor estimation.

Furthermore, the approach of the proposed mechanism in making sets of data nodes, hosting replicas of each file, can also be employed to distribute the namespace of a storage cluster among several metadata servers. As a result, the performance of metadata operations will be improved and failure of the NameNode does not prevent the other nodes from serving I/O requests.

The proposed mechanism is comprised of two agents, named RFEA and RFSA, which are responsible for estimating the proper replication factor and adapting files' replication factor to the remaining storage space respectively. Currently, a single replication factor is used for all data blocks of a file. Reducing granularity of the replication mechanism and gathering access patterns of data blocks rather than files can improve the overall performance of the data replication method. This will lead to a more aware replication mechanism that replicate the most popular data blocks and save lots of storage space hence. Moreover, it will also affect the network traffic of storage clusters by avoiding unnecessary replication operations.

Besides using access and host sets of each file, RFEA considers the execution state of reader nodes in determining their required number of replicas. Furthermore, a weighted-average is performed to reduce the impact of momentary access patterns on the replication factor estimation.

On the other hand, RFSA monitors I/O statistics of the cluster and provides RFEA with a parameter to adapt the replication process to the remaining storage space. A programming thread, called AdapT, is responsible for calculating this parameter and fulfills this task using AdapT+ and AdapT.

We have measured the performance of this mechanism using Hadoop framework and the results prove that it can improve the read throughput and response time of applications with long-term I/O operations.

As a conclusion, we have proposed a mechanism to estimate the proper number of replicas for each file based on its popularity in the storage cluster. Besides its compatibility with HDFS and adaptation to cluster storage state, this mechanism does not store any access history and requires low computational cost. Moreover, it does not increase network traffic due to using available statistics of the NameNode. These points are the novelties of the proposed mechanism and should be considered along with its performance improvements. Several possible ways to improve this mechanism and achieve higher I/O performance have also been stated in this section.

#### REFERENCES

- [1] B. Witworth, J. Fjermestad, and E. Mahinda, "The web of system performance," *Communications of the ACM*, vol. 49, no. 5, pp. 93-99, May 2006.
- [2] H. Stockinger, A. Samar, K. Holtman, I. Foster, and B. Tierney, "File and object replication in data grids," *Cluster Computing*, vol. 5, no. 3, pp. 305-314, Jul. 2002.
- [3] H. Lamehamedi, Z. Shentu, B. Szymanski, and E. Deelman, "Simulation of dynamic data replication strategies in data grids," in

*Proceedings of the International Parallel and Distributed Processing Symposium*, Nice, France, 2003.

- [4] H. Lamehamedi, B. Szymanski, Z. Shentu, and E. Deelman, "Data replication strategies in grid environments," in *Proceedings of the Fifth International Conference on Algorithms and Architectures for Parallel Processing*, Washington, DC, USA, 2002, pp. 378-384.
- [5] R. Buyya, *High Performance Cluster Computing*. Prentice Hall, 1999.
- [6] M. Lei, S. V. Vrbsky, and X. Hong, "An on-line replication strategy to increase availability in data grids," *Future Generation Computer Systems*, vol. 24, no. 2, pp. 85-98, Feb. 2008.
- [7] L. M. Khanli, A. Isazadeh, and T. N. Shishavan, "PHFS: A dynamic replication method, to decrease access latency in the multi-tier data grid," *Future Generation Computer Systems*, vol. 27, no. 3, pp. 233- 244, Mar. 2011.
- [8] H. Huang, W. Hung, and K. G. Shin, "FS2: Dynamic data replication in free disk space for improving disk performance and energy consumption," in *Proceedings of the Twentieth ACM Symposium on Operating Systems Principles*, New York, USA, 2005, pp. 263-276.
- [9] D. Teodosiu, N. Bjorner, J. Porkka, M. Manasse, and Y. Gurevich, "Optimizing file replication over limited-bandwidth networks using remote differential compression," Microsoft Research, 2006.
- [10] R.-S. Chang and H.-P. Chang, "A dynamic data replication strategy using access-weights in data grids," *The Journal of Supercomputing*, vol. 45, no. 3, pp. 277-295, Sep. 2008.
- [11] A. Do§an, "A study on performance of dynamic file replication algorithms for real-time file access in data grids," *Future Generation Computer Systems*, vol. 25, no. 8, pp. 829-839, Sep. 2009.
- [12] T. Loukopoulos and I. Ahmad, "Static and adaptive distributed data replication using genetic algorithms," *Journal of Parallel and Distributed Computing*, vol. 64, no. 11, pp. 1270-1285, Mar. 2004.
- [13] R.-S. Chang, H.-P. Chang, and Y.-T. Wang, "A dynamic weighted data replication strategy in data grids," in *IEEE/ACS International Conference on Computer Systems and Applications*, Doha, Qatar, 2008, pp. 414-421.
- [14] H. Shen, "An efficient and adaptive decentralized file replication algorithm in P2P file sharing systems," *IEEE Transactions on Parallel and Distributed Systems*, vol. 21, no. 6, pp. 827-840, Jun. 2010.
- [15] H. Sato, S. Matsuoka, T. Endo, and N. Maruyama, "Access-pattern and bandwidth aware file replication algorithm in a grid environment," in *9th IEEE/ACM International Conference on Grid Computing*, Tsukuba, Japan, 2008, pp. 250-257.
- [16] C.-T. Yang, C.-P. Fu, and C.-H. Hsu, "File replication, maintenance, and consistency management services in data grids," *The Journal of Supercomputing*, vol. 53, no. 3, pp. 411-439, Jul. 2009.
- [17] K. Shvachko, H. Kuang, S. Radia, and R. Chansler, "The Hadoop distributed file system," in *26th Symposium on Mass Storage Systems and Technologies (MSST)*, Incline Village, NV, 2010, pp. 1-10.
- [18] The Apache Software Foundation. (2012, Mar.) FileSystem (Hadoop 1.0.2 API). [Online]. http://hadoop.apache.org/common/docs/current/api/org/apache/hadoo p/fs/FileSystem.html

[19] T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein, *Introduction to Algorithms*, 3rd ed. MIT Press, 2009.

- [20] T. White, *Hadoop: The Definitive Guide, 2nd Edition*. O'Reilly Media / Yahoo Press, 2010.
- [21] The Apache Software Foundation. (2012, Mar.) Hadoop 1.0.1 Release Notes. [Online]. http://hadoop.apache.org/common/docs/r1.0.1/releasenotes.html

