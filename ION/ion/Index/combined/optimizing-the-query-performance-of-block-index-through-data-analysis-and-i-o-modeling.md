# **Optimizing the Query Performance of Block Index Through Data Analysis and I/O Modeling**

Tzuhsien Wu National Tsing Hua University Hsinchu, Taiwan hsien@lsalab.cs.nthu.edu.tw

Bin Dong Lawrence Berkeley National Lab Berkeley, CA dbin@lbl.gov

# Jerry Chou National Tsing Hua University Hsinchu, Taiwan jchou@lsalab.cs.nthu.edu.tw

Scott Klasky Oak Ridge National Lab Oak Ridge, TN klasky@utk.edu

Shyng Hao National Tsing Hua University Hsinchu, Taiwan shinhoward@lsalab.cs.nthu.edu.tw

Kesheng Wu Lawrence Berkeley National Lab Berkeley, CA kwu@lbl.gov

# **ABSTRACT**

Indexing technique has become an efficient tool to enable scientists to directly access the most relevant data records. But, the time and space requirements of building and storing indexes are expensive in the traditional approaches, such as R-tree and bitmaps. Recently, we started to address this issue by using the idea of "*block index*", and our previous work has shown promising results from comparing it against other well-known solutions, including ADIOS, SciDB, and FastBit. In this work, we further improve the technique from both theoretical and implementation perspectives. Driven by an extensive effort in characterizing scientific datasets and modeling I/O systems, we presented a theoretical model to analyze its query performance with respect to a given block size configuration. We also introduced three optimization techniques to achieve a 2.3x query time reduction comparing to the original implementation.

# **KEYWORDS**

Scientific data, Indexing, I/O system, Modeling, Performance analysis

#### **ACM Reference format:**

Tzuhsien Wu, Jerry Chou, Shyng Hao, Bin Dong, Scott Klasky, and Kesheng Wu. 2017. Optimizing the Query Performance of Block Index Through Data Analysis and I/O Modeling. In *Proceedings of SC17, Denver, CO, USA, November 12–17, 2017,* 10 pages. DOI: 10.1145/3126908.3126934

# **1 INTRODUCTION**

Massive amounts of scientific data is generated from scientific experiments, observations, and large-scale simulations in many domains, such as astronomy, environment, and physics. The size of these datasets typically ranges from hundreds of gigabytes to tens of petabytes [1]. Therefore, the ability to access only the necessary data records, instead of shifting through all of them,

*SC17, Denver, CO, USA*

© 2017 ACM. 978-1-4503-5114-0/17/11. . . $15.00

DOI: 10.1145/3126908.3126934

can significantly accelerate data analysis operations [23, 24]. The best-known technology for locating selected data records from a large dataset is with indexing techniques [22, Ch. 6], such as variants of B-trees [8] used in DBMS, bitmap indexes [28], and inverted indexes. However, the size of indexes produced from those techniques is often close to or even larger than the size of their original datasets [15]. As the volume of datasets continues to grow, indexes will even consume more computing time to build, more storage space to store, and most importantly more I/O bandwidth to access. The problem is further exacerbated by the increasing gap between I/O and compute [13], and the growing demand for real-time or *in situ* data analysis [18, 26].

In recent years, many efforts have been made to develop lightweight indexing methods [15, 16]. The goal is to reduce the time and space required for building and storing these indexes without sacrificing query performance. In prior work [29, 30], the idea *block index* was proposed based on the block range index technique [11]. The approach is motivated by the fact that scientific datasets are commonly stored and managed by parallel file systems and IO libraries, such as Lustre, HDF5 [25], NetCDF [27], and ADIOS [14]. In order to achieve greater scalability and throughput, these I/O management layers are optimized for large chunks sequential I/O instead of small random I/O. As a result, building fine-grained indexes to retrieve selected data records individually could become an expensive and inefficient approach [3]. Therefore, we proposed to build indexes at the data block level, and read data from the storage system in a unit of block. On one hand, it can greatly reduce the size of indexes. On the other hand, the block sequential I/O access pattern also improves I/O efficiency and simplifies I/O modeling. The implementations on HDF5 [30] and ADIOS [29] have demonstrated block index can deliver comparable query performance with much lower indexing cost and complexity in comparing to other popular data management tools, such as SciDB, and FastBit.

However, it not trivial how the best query performance of block index can be achieved on complex parallel file systems. In particular, the setting of block size presents a I/O performance tradeoff dilemma. Using a larger block size setting can obtain higher I/O throughput from the underlying storage system, but also cause more redundant data to be accessed. Therefore, this paper aims to analyze and optimize the query performance of block index by giving a tight upper bound analysis of the I/O requests from answering a query, and developing three optimization techniques

Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for components of this work owned by others than ACM must be honored. Abstracting with credit is permitted. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and/or a fee. Request permissions from permissions@acm.org.

![](_page_1_Figure_2.png)

**Figure 1: Traditional indexing strategy that causes expensive indexes and inefficient data access.**

based on the characteristics of scientific datasets and performance modeling of parallel file systems. The first optimization technique is called *merge read*. The idea is to maximize the I/O throughput at query time by reading multiple discontiguous hit blocks at once when their locations are close enough within a distance threshold. To find the proper threshold setting, we construct a performance model of Lustre, and show our model-driven decision can achieve close to optimal performance in real environment experiments. The second technique is called *adaptive dynamic schedule*. It aims to balance the data retrieval workload among reader processes. This technique overcomes the unstable I/O throughput of parallel shared file systems like Lustre, and ensures the aggregated I/O bandwidth from reader processes are fully utilized. Finally, the third technique is called *partial sort*. It exploits the idea of using a more costly index technique, such as inverted index, as the secondary index on a block to compensate the limitation of block index. As observed from our study of the real scientific datasets, the majority of hits are located in the blocks with higher variance values. Therefore, the query performance can be improved significantly by sorting a small amount(i.e., 5%) of the data blocks. At the end, we evaluate our approach using three real datasets on a Cray XC30 machine (NERSC Edison). At the end, our evaluation shows that our approach successfully improve query performance by up to a factor of 2.3 comparing to the original block index implementation.

The rest of paper is structured as follows. Section 2 introduces the block index technique. Section 3 gives the performance analysis and modeling of block index. Section 4 presents our three performance optimization techniques. The characteristics studies of scientific datasets are summarized in Section 5, and the experimental evaluation results are presented in Section 6. Finally, Section 7 is the related work, and Section 8 is the conclusion.

# **2 BLOCK INDEX OVERVIEW**

The goal of this work is to enable efficient range query with position and value retrieval. For instance, given a query, such as "temperature > 100", the data records that satisfy the query constraints are called hits, and we must retrieve the *positions* and the *values* associated of these hits. As shown in Figure 1, traditional indexing techniques tend to build heavy indexes which can locate the accurate position of each hit. However, retrieving scattered hit records often results in much slower query time due to the inefficient random I/O access on storage systems. To minimize the size of indexes and improve the efficiency of I/O, we proposed an indexing technique called "*block index*". In this section, we briefly review its basic design, strengths, and limitations based on the observations from the prior work [29, 30].

# **2.1 Basic Design**

The basic design of block index is relatively straightforward. It partitions a dataset into a set of non-overlapped fixed-size data chunks, called *blocks*. The indexes are built by recording the maximum and minimum values from each block. This simple form of block index is also called block range index [11]. Given block indexes, the query procedure consists of three steps: (1) index evaluation, (2) block retrieval, and (3) candidate check. In the first step, indexes are loaded and evaluated against the query range to identify the hit *blocks*, which are the blocks whose value range have an intersection with the query range. Then in the second step, the hit blocks are read from the storage system and loaded into the memory of reader processes. The data records in these hit blocks are also called, *candidates*. Finally, a check is performed on the list of candidates, and the data records outside query range are filtered. The positions and values of hits are then returned as the final query result.

Due to the simplicity of block index, it has the following advantages. (1) Since the indexes only store two values from each block, the total size of indexes is extremely small comparing to the size of the original dataset. Therefore, the time and space required for building, storing and loading these indexes are minimized. (2) Both query and index procedures only cause sequential I/O, and the minimum I/O size can be controlled by the user specified block size. Therefore, the I/O accesses can be handled by the underlying storage system more efficiently. (3) Because both query and index procedures can be performed independently on each block, this approach can be easily implemented in parallel to take advantage of the multi-core architecture and computing power of an HPC system.

This approach has been implemented using the ADIOS and HDF5 parallel I/O library on Lustre file system. The performance study has also shown that block index can achieve comparable or even better query performance than the existing methods, including SciDB [9] and FastQuery [7], when the hit values need to be retrieved.

# **2.2 Challenges and Proposed Solutions**

Although block index can be a lightweight yet efficient index technique for query data retrieval, we also identify three key research challenges for optimizing its query performance. We briefly discuss these challenges in below, and the details of our modeling and optimizations are described in Section 3 and Section 4, respectively.

(1) *How to decide the proper block size to achieve better I/O throughput efficiency?* The block size setting is critical to query performance, but it is also a difficult dilemma because of the performance tradeoff it presents. Using a larger block size setting can obtain higher I/O throughput from the underlying storage system, but also require accessing more redundant data. The best setting depends on many factors, including the I/O performance characteristics, query selectivity, hit positions, etc. Therefore, in prior work [30], the best setting was only found experimentally. In this paper, we address this challenge in two ways. First, in Section 3, we present a theoretical analysis of the block index by providing a tight upper bound on the size of accessed data and the number I/O requests for answering a query with a given query selectivity. Combining this model with the underlying storage system performance model can provide an estimated query performance. Second, in Section 4.1,

Optimizing the Query Performance of Block Index SC17, November 12–17, 2017, Denver, CO, USA

![](_page_2_Figure_1.png)

**Figure 2: An illustration of I/O access from the query process of block index. According to the term defined in our model, there are 7 selected blocks, 3 counting groups with 2 selected blocks each and 4 (=7-3) islands.**

we propose a technique to improve I/O throughput efficiency by merging the read requests at query time. With this approach, we can choose a smaller block size to reduce redundant data, and then merge those small blocks into a single large I/O requests to obtain higher I/O throughput from the storage system. As shown in our experimental results in Section 6.1, our approach can break the dilemma by ensuring query performance can always be improved when using a smaller block size setting.

(2) *How to prevent redundant data from a block to reduce the total data read size (i.e., the number of candidate records)?* Clearly, one of the main drawbacks of block index is that the whole data block must be retrieved when it only contains a few number of hits. Therefore, we decided to exploit the idea of using a more costly index technique, such as inverted index, as the secondary index on a block to compensate the limitation of block index. As detailed in Section 4.3, our approach sorts the records in the block, then builds an inverted index to store their original record positions. Thus, only the data within the query range will be retrieved, and both the values and positions of hit records can be retrieved in a single I/O request. However, because the inverted index is costly, we could only afford to build it for a few blocks. So we studied the characteristics of scientific datasets in Section 5, and decided to build inverted indexes on the block with higher variance values.

(3) *How to balance the I/O workload among reader processes to maximize I/O bandwidth utilization?* In order to fully utilize the I/O bandwidth for data retrieval, the I/O workload among reader processes needs to be balanced. But it is not a trivial task in a real large-scale HPC system where the storage system is shared among users, and the data is managed by a complex parallel file system like Lustre. Therefore, we propose several scheduling algorithms to address this problem in Section 4.2, and show the adaptive dynamic scheduling algorithm can achieve the best performance in Section 6.2.

# **3 BLOCK INDEX PERFORMANCE MODELING**

In this section, we present a theoretical analysis of the block index by providing a tight upper bound on the size of accessed data and the number I/O requests to answer a query. We prove these two I/O metrics can be modeled as a function of query selectivity (i.e., the fraction of dataset that is selected by the query) and block size. It is well known that the parallel I/O performance on storage systems is influenced by several tuning parameters [2], and difficult to be modeled or predicted. However, our theoretical results can serve as an implication to the I/O performance, and understand the performance tradeoff of the block size.

| Table 1: Variables in the formula for estimating the I/O ac |
| --- |
| cess behavior of a block index |

| N | Number of rows/records of the dataset |
| --- | --- |
| B | Block size in bytes |
| w | Word size in bytes |
| s | Query selectivity |
|  | (i.e., the fraction of dataset is selected) |
| S | The probability that a block is selected |
|  | (i.e., at least one data record in the block is selected.) |
| V | Volume of data to be read (in bytes) |
| R | Number of read operations. |

For block index, its query time is dominated by the time from retrieving blocks that contain selected records, and its I/O access can be illustrated by the example in Figure 2. Here we assume consecutive selected blocks are read by a single I/O operation to reduce I/O requests. For the purpose of our discussion, we also define a group of consecutive selected blocks as an *island*, and define every two-block group as a *counting group*. Given a particular query, the maximum number of selected blocks, and the maximum number of islands is given by a type of random data with independent and identically distributed (i.i.d.). In which case, the probability of a record got selected by a query is independent and identical to the probability of any other record. In scientific datasets, such as climate data, records stored in near locations tend to have similar values. On such datasets, the number of selected blocks would be smaller than i.i.d. data. Therefore, the query time of block index is likely to be shorter than with random data.

The parameters used in our model are summarized in Table 1. In the following analysis, we first show the probability of a block get selected is S = 1 − (1 − s) B/w in Proposition 3.1. Then based on the block selectivity S, we derive the total volume of read bytes V , and the number of I/O requests R as proven in Proposition 3.2 and Proposition 3.3, respectively.

Proposition 3.1. *The probability that a block contains a hit is* S = 1 − (1 − s) B/w .

Proof. A block has B/w data records. Given selectivity s, a block is not accessed if none of the records is selected, and the probability that a single record is not selected is (1 − s). Assuming the data records are i.i.d. random variables, then the probably that none of the B/w records is selected is (1 − s) B/w . Thus, the probability that a block is accessed because of some of the records are selected is S = 1 − (1 − s) B/w . -

Proposition 3.2. *The total number of bytes that needs to be read for answering a query with selectivity s, data size* N *and block size* B is V = B- N w B (1 − (1 − s) B/w ).

Proof. Given N records of w bytes each, the number of blocks from the dataset is - N w B . As proven in Corollary 3.1, the probability of a block to be accessed is (1 − (1 − s) B/w ). Thus the total number of accessed blocks is - N w B (1 − (1 − s) B/w ). Since all the data needs to be read from disk when its block is selected, the total number of bytes to read is V = B- N w B (1 − (1 − s) B/w ). -

![](_page_3_Figure_2.png)

**Figure 3: Comparison of results from theoretical model and experimental observations. The number of read bytes can be computed as the number of blocks multiplied by the block size in (a). The matching lines indicate our model can accurately characterize the I/O access of block index.**

Proposition 3.3.: _The number of read requests is $R=\frac{V}{B}-(\lceil\frac{Nw}{B}\rceil-1)(1-(1-s)^{B/w})^{2}$_

Proof. As can be observed from the illustration in Figure 2, the number of read operations is the same as the number of islands, and the number of islands can be computed by the number of selected blocks minus the number of counting groups. This is because for any island with L numbers of selected blocks, it contains L − 1 number of counting groups. Therefore, for each island, if we subtract the number of selected block by its number of counting group, we can always get the result of 1. Since the selected blocks of each island are not overlapped, the total number of islands can be computed by the total number of selected blocks minus the total number of counting groups.

In Proposition 3.2, we already proved the total number of read bytes V can be derived from our model. Thus the total number of selected blocks can be computed as V /B. On the other hand, from Proposition 3.1, we have also shown the probability of a block to be selected can be computed as S = 1− (1−s) B/w . Since the selectivity of a block is independent of other blocks, the probability of two consecutive blocks are both selected is S2. Therefore, the number of counting group can be computed as (- N w B − 1)(1 − (1 −s) B/w ) 2. Combining the two results above, we know the number of islands (i.e., the number I/O requests) is R = V B − (- N w B − 1)(1 − (1 − s) B/w ) 2. -

To demonstrate what can be derived from our theoretical model, we execute queries on a uniform random synthetic dataset and compare the I/O statistics observed from the experiments to the ones computed from our model. The results of query selectivity 0.001 under various block size settings are shown in Figure 3. In the plot, we use dots to depict the experimental results, and use a line to indicate the theoretical results. As shown, all the dots in the figure fall closely to the line. Therefore, it shows that our theoretical model can accurately characterize the I/O access of block index. From the figure, we can also observe the performance impact of block size setting. As the block size increases, a larger amount of data is read from a file, but fewer number of I/O operations are issued. Therefore, a proper block size should be chosen for a given query selectivity accordingly.

# **4 BLOCK INDEX OPTIMIZATION**

# **4.1 Merge Read**

According to our analysis in the previous section, pre-determining the optimal block size at indexing time is difficult because it depends on the actual hit positions which cannot be known in prior. Therefore, we tackle the problem from another angle to maximize I/O performance by merging hit blocks at query time.

As described in Section 2.1, after the first query step, the hit blocks are identified by evaluating the block indexes against the query range. For instance, let Figure 4 indicate the locations of all the hit blocks from a query. The hit blocks can be retrieved in several different ways. We could use 7 I/O requests to read these hit blocks individually. Or we could merge contiguous hit blocks in a single request, and read them in 4 I/O requests (as depicted in the blue boxes). Or we could even merge discontiguous blocks into a single request, and read all the hit blocks in just 2 I/O requests (as depicted in the red boxes). Therefore, our goal is to determine a set of I/O requests that can retrieve all the hit blocks in the shortest time.

To find the optimal set of I/O requests, we prove that it is the same as finding an optimal merge threshold, δ, when the I/O time of a request is modeled as T (n) = α + n/β where n is the size of I/O request, α is a constant I/O latency, and β is the I/O bandwidth. Accordingly, we can find the optimal solution in linear time by simply scanning through the hit blocks in the order of their positions, and merging the ones within the merge threshold into a single I/O request.

Our proof consists of three parts. First, in Corollary 4.1, we prove that two individual hit blocks should always be merged if their distance is less or equal to α · β/B, where B is the block size in bytes. Next, in Corollary 4.2, we prove that given a set of hit blocks that have been merged by a threshold δ = α · β/B, splitting them will always cause longer I/O time. Similarly, we can prove any merged request that contains blocks with a distance larger than the merge threshold δ = α · β/B should be split (The proof is omitted from the paper due to space limit.). Concluded from the three proofs above, we know that the optimal I/O time is achieved if and only if all the blocks within the merge threshold (i.e., δ = α · β/B) are merged into the same I/O request.

Corollary 4.1. *Given two hit blocks with block size* B*, and separated by* d *blocks in between, we should merge them to achieve shorter I/O time when* d ≤ α · β/B.

Proof. According to the I/O performance model, if the two blocks are read separately, their I/O time is t = 2 × (α + B/β). On the other hand, if they are merged into a single I/O request, the I/O time is t = α + (2 + d) × B/β. Therefore, t ≤ t if and only if d ≤ α · β/B, which means two blocks should be merged by their distance is less or equal to α · β/B. -

Corollary 4.2. *Given a set of hit blocks that have been merged into a single I/O request by a merge threshold* δ = α · β/B*, split the request cannot reduce I/O time.*

Proof. Let n be the number of hit blocks that are merged in the request, and the distances between these hit blocks are {d1, ··· ,dn−1}, where di ≤ α · β/B, ∀i.

Optimizing the Query Performance of Block Index SC17, November 12–17, 2017, Denver, CO, USA

* [10] Merge contiguous bit blocks into a single request.
* [11] Merge continuous bit blocks into a single request.

**Figure 4: An example of merge read technique. The black boxes are hit blocks after evaluating indexes at query time. The blue boxes indicate the I/O requests when the contiguous hit blocks are merged. The red boxes indicate the I/O requests when the discontiguous hit blocks are also merged.**

Assume the request is split to two requests at an arbitrary position k, such that the first request reads blocks 1 ∼ k, and the second request reads blocks (k + 1) ∼ n. Accordingly, the I/O time before splitting is

$$t=\alpha+(n+\sum_{1}^{n-1}d_{i})\times B/\beta$$

On the other hand, the I/O time after splitting is

$$t^{\prime}=2\times\alpha+(n+\sum_{1}^{k-1}d_{i}+\sum_{k+1}^{n-1}d_{i})\times B/\beta$$

Therefore, t−t = α −dk ×B/β. Since dk ≤ α ·β/B, we get t−t ≥ 0, which means no matter where we split the request, it cannot reduce I/O time. -

After proving the existence of merge threshold δ, we benchmark the Lustre file to find the values of α and β in the I/O performance model. As shown in Figure 5, the I/O throughput does increase linearly to the read size. This behavior indicates the I/O time can be captured by the I/O model used in our analysis. However, as expected, the values of α and β are heavily dependent on the I/O contention on the Lustre OST (i.e., object storage node). As we increase the number of reader processes on the same OST, the I/O throughput starts to degrade. Also, interestingly, we found the performance degradation will be much less if it is the same data block read by the processes as shown in Figure 5 (a). We believe it is likely due to the cache effect on Lustre and other storage layers.

In the case of our query data retrieval process, we never retrieve the same block twice, so we only need to consider the performance results in Figure 5 (b). To estimate the concurrent access on OST, we assume the hit blocks are scattered evenly across OSTs and read by any process with equal probability. In this case, the expected concurrent access on an OST is the number of total read processes divided by the file stripe count (i.e., the number of OSTs for storing a file).

In sum, regardless what block size is used to build the indexes, we can use the merge read technique to reduce the number of concurrent reads to achieve the best I/O performance. The merge decision is done in linear time, and controlled by a simple merge threshold. The threshold only depends on the parameter of our I/O performance model, the block size, and the I/O parallelism settings. All these parameters can be obtained as explained in this subsection, and our experiments prove that our pre-determined threshold value can indeed achieve the best query performance in practice.

![](_page_4_Figure_12.png)

(a) Same read location on the same OST. (b) Different read location on the same OST.

**Figure 5: Performance modeling of Lustre file system for concurrent read access on the same OST. Both the record size of a read request and stripe size of Lustre file system are set to 1MB.**

# **4.2 Adaptive Dynamic Schedule**

It is well-known that the workload must be balanced to fully utilize the system capacity in a large scale HPC system. Therefore, to maximize the I/O bandwidth utilization for retrieving the hit blocks, we also have to balance the I/O workload among reader processes. To reach that goal, we introduce a scheduling step after the hit blocks are identified and merged into a set of I/O requests. The scheduler is responsible for dispatching these I/O requests (i.e., tasks) to processes (i.e., workers) in a more efficient and fair manner. We implemented three scheduling algorithms, namely the *static*, *dynamic*, and *adaptive dynamic* schedulers. We introduce these algorithms below, and compare their performance in Section 6.2.

Static scheduler evenly partitions tasks among processes, and sends the list of assigned tasks to each process in a single message before data retrieval step. In contrast, dynamic scheduler only schedules one task to a process at a time, and workers dynamically request the next task after they complete the previously assigned tasks. Observed from our experimental study, both schedulers performed poorly in practice. Static scheduler failed to balance the workload because the file system is shared among compute nodes, and I/O requests are queued in an arbitrary order by the storage system. As a result, I/O requests may encounter unpredictable I/O latency delay at runtime. Especially, the latency variation becomes more apparent when the scale of parallelism increases. On the other hand, dynamic scheduler suffers from significant communication and computation overhead at the master node, especially when the number of workers increases or the number of hit blocks increases under a higher query selectivity or a smaller block size.

To overcome the aforementioned issues, we propose an *adaptive dynamic* scheduler, which combines the strengths of both static and dynamic schedulers. The proposed scheduling algorithm is controlled by two parameters θ and λ. Variable θ denotes the percentage of the selected blocks that are scheduled evenly and statically like the static scheduler. The rest of blocks are scheduled dynamically. Furthermore, instead of assigning a fixed number of blocks (or chunk size) to one worker at a time, we use an exponential back-off strategy to decrease the scheduling chunk size over time. Specifically, the chunk size is computed as - π (λ∗(n−1)) where π

![](_page_5_Figure_2.png)

**Figure 6: The indexes built by the partial sort technique.**

denotes the number of remaining blocks needing candidate checks, and n is the number of workers. The value of λ must be larger than 1 (i.e., It is set to 2 in our experiments), and a larger value implies fewer number blocks are assigned in each round of assignments. Hence, the scheduling chunk size decreases every time a new job has been assigned, and a smaller chunk size will be chosen at the end to balance the load more evenly. At the same time, the scheduling overhead between master and workers can be mitigated, and the random access patterns can be avoided because of the larger chunk size used at the beginning. Furthermore, our adaptive dynamic scheduler also consider the varied read size of I/O requests (i.e., caused by the merge read and partial sort techniques), and the OST location of these I/O requests, so that the workload can be more evenly distributed, and the concurrent access on the same OST can be minimized. Our evaluation results in Section 6.2 clearly shows the adaptive dynamic scheduler can significantly improve workload balancing and query performance.

# **4.3 Partial Sort**

Partial sort is a technique that exploits the idea of using the inverted index as the secondary index on blocks, so that we don't need to read the whole block when it only contains a few number of hits. As shown in Figure 6, the inverted index of a block contains the sorted record values from a block, and their record positions in the original dataset. In addition, we build a lookup table to accelerate the search time of inverted index. The lookup table contains only a few record values from the inverted index, so it can be loaded into memory and evaluated quickly to find the part of inverted indexes that should be retrieved for a query. However, building inverted index is expensive due to its indexes size. Therefore, our approach only builds the inverted indexes for a small percentage of the blocks. According to our study on the real datasets in Section 5, we prefer to choose the blocks with higher variance values because these blocks have a higher probability of containing hits.

We integrate the inverted index with block index as follows. In the indexing procedure, besides building the block index for each block, we also evaluate the variance of a block. If the variance is higher than a given threshold, we then build the inverted indexes for the block, and add a flag in the block index entry to indicate the block is sorted. In the query procedure, first we evaluate the block index to identify the hit blocks. Then the flag in the block index entry is checked to determine the block is sorted or not. If the block is not sorted, we have to retrieve the whole block from the original dataset. Otherwise, we can read the partial block from the sorted dataset to reduce the I/O amount. Both the inverted index and block index techniques only generate sequential I/O accesses, therefore the merge read and load balancing techniques mentioned above can still be applied to further optimize their I/O requests.

#### **5 DATASETS CHARACTERISTICS STUDY**

This section introduces the scientific datasets in our study, analyzes their characteristics, and discusses how these characteristics can affect the design of our block index technique.

# **5.1 Datasets**

Three real scientific datasets were used in our study as described below.

**VPIC** dataset is produced by a plasma physics simulation [4]. The original dataset contains records of 1 trillion particles, and each particle is associated with seven one-dimensional variables describing its location and energy. In our experiments, we use a subset dataset with 188 billions particles. But it is still the largest dataset in our test, and the file size is around 700GB. In the evaluations, we use a query to find the particles with the highest energy level.

PTF dataset is from a real cosmology observations database, called the Palomar Transient Factory. For our experiments, we converted the records from the database into an HDF5 data format file. It is a one-dimensional dataset with 930 million records, and its file size is 3.75GB. Our evaluated query is to find the planets with the dimmest planets in the astronomy observations by searching the records with the highest magnitude scale values.

CAM is a climate dataset output from the Community Atmospheric Model (CAM5.1). The dataset is a 3650x128x256 threedimensional dataset associated with time, latitude and longitude. Our query aims to find the region with the highest precipitable water values across all the time recorded in the dataset. Although CAM output results into lots of timesteps, the dataset size of each timestep is rather small, thus its file size is only 458MB.

# **5.2 Data locality**

As known, block index must retrieve the whole block when it contains any hit. If the distance between hits is closer, more hits are likely to be contained in a single block, and the efficient of data retrieval can be improved. On the other hand, if the hits are evenly scattered across the dataset, it will be the worse case scenario for block index as we analyzed in Section 3. Therefore, the locality of hits is crucial to the query performance of block index, and we analyze this data characteristic in this subsection.

We studied the data locality of our datasets by analyzing the distance between any pair of neighboring hits according to their serialization positions on storage devices. If a dataset has strong locality with respect to a query, the hits should locate close to each other, and the resulting hit distances should be smaller. In Figure 7, we plot the cumulative distribution function (CDF) of these hit distances under varied query selectivities. The hit distances shown in the plot are normalized to the size of the dataset, so we can compare the locality between different datasets more easily (i.e., excepting the CAM dataset is too small, so the distance values are the number of records). We also plot the locality of a synthetic dataset with uniformly distributed random numbers in Figure 7 (d) as the worst case comparison result.

As shown by Figure 7, CAM dataset has the strongest locality, because 60% of hits are located right next to each other in the case of 1e-4 query selectivity. Even under 1e-6 query selectivity, we still found 37% of hits are contiguous. Comparing to the synthetic

![](_page_6_Figure_2.png)

**Figure 7: CDF of data locality under different query selectivities. Data locality is measured by the distance between the two neighboring hits. The distance is normalized to the total size of the dataset for PTF and VPIC.**

![](_page_6_Figure_4.png)

**Figure 8: CDF of the variance of data blocks. The black dots on the curve show the hit blocks under** 10−4 **query selectivity.**

dataset, PTF and VPIC still have much better locality. For instance, more than 95% of hit distances are within 100 records for the PTF dataset when the query selectivity is 1e-4. The VPIC dataset has weaker locality because its records are sorted by the particle ID which has little correlation to the search value of our query. In sum, many scientific datasets, like CAM and PTF, exhibits the characteristic of data locality, and the block index can take advantage of this characteristic to deliver better query performance.

# **5.3 Data variance**

Next, we analyze the data variance characteristic of datasets to explain why we decided to sort the blocks with higher variance values, and how many percentages of blocks should be sorted. Figure 8 plots the CDF of blocks against their corresponding variance values. The variance of a block is calculated asV ar(X) = N i=1 (xi − μ) 2/N, where N is the number of records in a block, xi means the value of the i th record, and μ is the mean of X. We also depict the red dots in the figure to indicate the blocks with hits when the query selectivity is 1e-4. From the results of CAM and PTF datasets, we can observe that most of the hit blocks are the ones with higher variance values. Especially for the CAM dataset, the variance values of all the hit blocks are ranked in the top 10%. Therefore, by sorting this small amount of blocks with higher variance values can improve query performance greatly. On the contrary, for VPIC dataset, because its record values are more uniform distributed, the variance is much higher for most of the blocks. As a result, we did not observe a clear correlation between the variance and hit probability of a block. In this case, sorting blocks can still improve query performance. But

as shown by the experimental results in Section 6.3, the cost of building the indexes will likely grow proportionally as well.

# **6 EXPERIMENTAL EVALUATIONS**

Our experiments were conducted on the Edison supercomputer, a Cray XC30 machine. The datasets and queries for our evaluations have been described in Section 5.1. Both the data and index files were stored on a Lustre file system and striped across multiple OSTs storage nodes. In the rest of section, we first present the query performance improvement from each of our optimization techniques individually, then discuss the overall improvement at the end.

# **6.1 Merge Read**

For the merge read technique, we use experimental results to prove two propositions we made in Section 4.1. First, our proposed merge read method can improve I/O throughput, and the optimal merge threshold value can be determined in advance according to our theoretical analysis and performance modeling results. Second, merge read technique can solve the I/O throughput problem of having a small block size setting, so the block size setting will no longer cause a tradeoff to the query performance.

To prove the first proposition, we plot the I/O throughput of hit blocks retrieval under varied merge threshold distance in Figure 9. As shown in the figure, merging hit blocks can indeed improve I/O throughput. But if the threshold is too large, the I/O throughput starts to decline because of the increasing data read size from accessing the redundant blocks. However, the optimal threshold setting derived from our proposed method can accurately estimate the I/O

![](_page_7_Figure_2.png)

**Figure 9: The data retrieval I/O throughput of merge read approach under varied merge distances.**

**read technique to the query throughput under varied block size settings.**

![](_page_7_Figure_5.png)

the minimum process execution time. A lower ratio indicates more balanced load. Adaptive Dynamic scheduler.

**Figure 11: Load balancing and performance comparison between different scheduling algorithms.**

throughput and achieve close to optimal results as shown by the dot marked in the figure. Noted, in this set of experiments, depending on the size of datasets, we also used a different number of reader processes and Lustre stripe count. Therefore, the robustness of our method can also be seen.

To prove the second proposition, we evaluated the query performance under different block size setting, and observed how the merge technique changes the results. Our results for the VPIC dataset is shown in Figure 10. The results of other datasets are similar, so we omit them from the paper. As shown by the results, without merge read technique, the query time grows when the block size setting is too large or too small, because of the tradeoff between I/O throughput and data read size. Also, as discussed in Section 3, the optimal block size setting is depending on the query selectivity and hit locations, so it is difficult to be determined at indexing time. In contrast, with merge technique, using a smaller block size can reduce redundant data access without suffering from the I/O throughput problem. So the block size setting will no longer cause a tradeoff to the query performance as expected.

# **6.2 Adaptive Dynamic Schedule**

We present our evaluation results using the VPIC datasets with 144 reader processes for a query with 1e-6 query selectivity. We compare the three proposed scheduling algorithms by plotting the CDF (cumulative distribution function) of the reader process against their own execution time in Figure 11(a). For the adaptive dynamic scheduler, its maximum execution time of a process is less than 0.5 seconds, and more than 90% of processes execute between 0.22 ∼ 0.3 seconds. In contrast, the process execution time

of static scheduler spreads widely from 0.4 seconds to 0.8 seconds, and the maximum execution time reaches over 1.5 seconds. The dynamic scheduler is more balanced than static scheduler, and most processes execute between 0.8 to 1 seconds. However, dynamic scheduler actually has the slowest average execution time because it suffers from the performance bottleneck on scheduling and the ineffective I/O performance of scattered data access. Therefore, adaptive dynamic scheduler clearly outperforms other scheduling algorithms in terms of load balancing and overall query performance.

Next, we exam our results under varied query selectivities. Figure 11(b) and Figure 11(c), summarize the results for load-balancing and performance, respectively. In Figure 11(b), we divide the maximum process execution time by the minimum execution process time as a metric to measure load balancing. If the value is closer to 1, it implies that all processes have a similar execution time, and the load is more balanced. As shown by the results, across all query selectivities, we can reach the same conclusion that static scheduler has the worst load balancing result, and the dynamic scheduler has the worst performance results. One interesting observation is that the load did become less balanced for adaptive dynamic scheduler when the query selectivity decreases. This is because there are fewer read operations, and thus fewer opportunities for our exponential back-off strategy to balance the load. But adaptive dynamic scheduler will never be worse than the dynamic scheduler. Finally, the significant query performance improvement shown in Figure 11(b) (c) indicates the importance of our proposed optimization technique.

#### Optimizing the Query Performance of Block Index SC17, November 12–17, 2017, Denver, CO, USA

![](_page_8_Figure_2.png)

**Figure 12: Query throughput of partial sort approach under varied percentages of sorted blocks.**

![](_page_8_Figure_4.png)

**Figure 13: Data read size of partial sort approach under varied percentages of sorted blocks.**

# **6.3 Partial Sort**

Figure 12 compares the query throughput when the percentage of sorted blocks is increased from 0% to 5% and 50%. Overall, when more blocks are sorted, the query performance becomes better because the amount of data that needs to be read from the file is reduced as more hit blocks can be read from the sorted file. This reduction of data read size can be seen from Figure 13. However, in several cases, we also found that sorting 50% of blocks didn't perform the best due to two reasons. First, searching the inverted indexes for the sorted blocks caused a certain amount of additional overhead. This overhead grows proportionally to the percentage of sorted blocks. Second, the amount of data read size reduction may not grows that much when the percentage of the sorted block is increased, especially when the query selectivity is higher or the locality of a dataset is stronger. This is mainly because of the data characteristics we found from the datasets where most hits are located in the blocks with higher variance values. Overall, partial sort approach improves query performance at the cost of increased index size and additional overhead. However, we could gain a significant performance improvement from sorting a small number of blocks when we know what are the blocks more likely having hits. In the case of CAM and PTF datasets, sort the blocks with top 5% of variance values give us comparable or better results than sorting 50% of the blocks.

# **6.4 Overall Performance**

Finally, Table 2 summarizes the query performance speedup over the non-optimized index implementation. The query selectivity used in this evaluation is 1e-3. The merge threshold used for CAM, VPIC is 6 blocks, and the threshold used for PTF is 8 blocks. For

| Table 2: Query performance speedup over the original non |
| --- |
| optimized block index implementation. |

|  | load balancing | partial sort | merge read | overall |
| --- | --- | --- | --- | --- |
| CAM | 1.49 | 1.98 | 1.45 | 2.28 |
| PTF | 1.40 | 1.88 | 1.76 | 2.03 |
| VPIC | 1.27 | 1.30 | 1.27 | 1.42 |

all the datasets, 5% of the blocks by the partial sort technique. As shown by the numbers in the table, the performance speedup varies between 1.27 ∼ 1.98 for each individual optimization technique. In general, we achieve higher speedup for the CAM dataset because it has strong data locality, and more serious load imbalance problem. The merge read technique improves the PTF dataset the most because the hits of VPIC are too scattered, and the hits of CAM are mostly in a single block. Partial sort technique can offer greater speedup than the other two, but it is at the cost of greater index size and time. Finally, we did achieve the highest speedup when all three techniques were used together. We haven't spent much effort tuning the integrated implementation, so we expect the speedup could be even better. But even for the VPIC dataset, we achieved a factor of 1.42 speedup.

# **7 RELATED WORK**

A variety of indexing techniques are available in popular database systems [21], many of which are variations of the B-Tree [8]. The B-Tree data structure is designed to update quickly as the underlying data records are modified. But scientific data is mostly accessed in a read-only manner, and thus bitmap index is a more appropriate indexing structure [20, 22]. A number of different strategies have been proposed to reduce the sizes of bitmap indexes and improve

their overall effectiveness. A state-of-art bitmap index technique is FastBit [28], and its parallel implementation FastQuery [7] has shown the capability of indexing and analyzing of trillion particle datasets [5]. However, building these complex data structures is time-consuming and the size of indexes is too large to fit in memory.

Recently, there were several attempts to design new indexing technique to reduce the index size based on data compression and reorganization. ISABELA [17] adapts B-splines curve fitting to compress data, and guarantees a user-specified point-by-point compression error bound by storing the relative errors between estimated and actual values. DIRAQ [15] exploits the redundancy of significant bits in the floating-point encoding among similar values, and uses a compressed inverted index to reduce index size. However, the data query is only a part of a data analysis workflow. Hence reorganizing and encoded data may have severe impacts to other processing steps.

Block index is a variation of the block range index(BRIN) technique proposed by Herrera in 2013 [11]. This technique is intended to enable very fast scanning of extremely large tables. Since the implementation of this technique is tightly coupled to the underlying storage and I/O systems, only ProstgreSQL has announced this feature in their products [11]. Other vendors have only described similar features, such as the storage index of Oracle [19] and Hive [12], the zone maps of Netezza [10]. Other recent studies [6, 30] have shown such technique is suitable for scientific datasets, because of the data locality from the spatial-temporal data similarity in these datasets. Instead of focusing on the implementation of this technique, our work provides valuable analysis and modeling results for block index, and justify how its performance can be optimized on HPC systems.

# **8 CONCLUSION**

This work made several contributions to analyze and optimize the query performance of block index technique on HPC systems. First, we present a theoretical analysis of the block index by providing a tight upper bound on the size of accessed data and the number I/O requests to answer a query. Then we propose three optimization techniques based on the characteristics of scientific datasets and the model of the Lustre file system. Our proposed solutions address several interesting and critical research questions. (1) The merge read technique eliminates the performance tradeoff of block size setting by ensuring smaller block size can achieve shorter data retrieval time. (2) The adaptive dynamic scheduling technique overcomes the unpredictable performance natural of a shared parallel file system, and maximizes the I/O bandwidth utilization. (3) The partial sort technique shows how block index can be integrated with a more costly indexing technique, like inverted index, to achieve better query performance at the limited cost of indexing. Our evaluation using three real scientific datasets on the Edison supercomputer proves our optimization can achieve a query performance speedup by a factor of 1.4 ∼ 2.3. We also believe our proposed I/O techniques and models can be useful to address similar random data access problems encountered in other data management fields besides query systems.

# **REFERENCES**

[1] IPCC Fifth Assessment Report. http://en.wikipedia.org/wiki/IPCC Fifth

- [2] B. Behzad, H. V. T. Luu, J. Huchette, S. Byna, Prabhat, R. Aydt, Q. Koziol, and M. Snir. Taming parallel i/o complexity with auto-tuning. In SC, pages 68:1–68:12, 2013.
- [3] S. B. Bin Dong and K. Wu. "spatially clustered join on heterogeneous scientific data sets". In *2015 IEEE International Conference on Big Data (IEEE BigData 2015)*, 2015.
- [4] K. J. Bowers, B. J. Albright, L. Yin, B. Bergen, and T. J. T. Kwan. Ultrahigh performance three-dimensional electromagnetic relativistic kinetic plasma simulation. *Physics of Plasmas*, 15(5):7, 2008.
- [5] S. Byna, J. Chou, O. Rubel, Prabhat, H. Karimabadi, W. S. Daughton, V. Royter- ¨ shteyn, E. W. Bethel, M. Howison, K.-J. Hsu, K.-W. Lin, A. Shoshani, A. Uselton, and K. Wu. Parallel I/O, analysis, and visualization of a trillion particle simulation. In SC, page 59, 2012.
- [6] C. Chen, X. Huang, H. Fu, and G. Yang. The chunk-locality index: An efficient query method for climate datasets. In *Parallel and Distributed Processing Symposium Workshops PhD Forum (IPDPSW), 2012 IEEE 26th International*, pages 2104–2110, May 2012.
- [7] J. Chou, M. Howison, B. Austin, K. Wu, J. Qiang, E. W. Bethel, A. Shoshani, O. Rbel, and P. R. D. Ryne. Parallel index and query for large scale data analysis. In *2011 International Conference for High Performance Computing, Networking, Storage and Analysis (SC)*, pages 1–11, Nov 2011.
- [8] D. Comer. Ubiquitous b-tree. *ACM Comput. Surv.*, 11(2):121–137, June 1979.
- [9] P. Cudre-Mauroux, H. Kimura, K.-T. Lim, J. Rogers, R. Simakov, E. Soroush, P. Velikhov, D. L. Wang, M. Balazinska, J. Becla, D. DeWitt, B. Heath, D. Maier, S. Madden, J. Patel, M. Stonebraker, and S. Zdonik. A Demonstration of SciDB: A Science-oriented DBMS. *Proc. VLDB Endow.*, 2(2):1534–1537, Aug. 2009.
- [10] G. S. Davidson, K. W. Boyack, R. A. Zacharski, S. C. Helmerich, and J. R. Cowie. Data-centric computing with the netezza architecture. Technical Report SAND2006-3640, Sandia National Laboratory, 2006.
- [11] A. Herrera. Minmax indexes. pg hackers.
- [12] Apache hive. https://hive.apache.org/.
- [13] S. Klasky, H. Abbasi, et al. In Situ Data Processing for Extreme-Scale Computing. In *SciDAC*, July 2011.
- [14] ADIOS. http://www.nccs.gov/user-support/center-projects/adios/.
- [15] S. Lakshminarasimhan, D. A. Boyuka, S. V. Pendse, X. Zou, J. Jenkins, V. Vishwanath, M. E. Papka, and N. F. Samatova. Scalable in situ scientific data encoding for analytical query processing. In *HPDC*, pages 1–12, 2013.
- [16] S. Lakshminarasimhan, J. Jenkins, et al. ISABELA-QA: Query-driven analytics with ISABELA-compressed extreme-scale scientific data. In SC, pages 1–11, Nov 2011.
- [17] S. Lakshminarasimhan, N. Shah, S. Ethier, S. Klasky, R. Latham, R. Ross, and N. F. Samatova. Compressing the Incompressible with ISABELA: In-situ Reduction of Spatio-temporal Data. In *Euro-Par*, pages 366–379, 2011.
- [18] K.-L. Ma. In situ visualization at extreme scale: Challenges and opportunities. *Computer Graphics and Applications, IEEE*, 29(6):14–19, Nov 2009.
- [19] A. Nanda. Smart scans meet storage indexes. *Oracle Magazine*, 2011.
- [20] P. O'Neil. Model 204 architecture and performance. In *2nd International Workshop in High Performance Transaction Systems, Asilomar, CA*, volume 359 of *Lecture Notes in Computer Science*, pages 40–59. Springer-Verlag, Sept. 1987.
- [21] P. O'Neil and E. O'Neil. *Database: principles, programming, and performance*. Morgan Kaugmann, 2nd edition, 2000.
- [22] A. Shoshani and D. Rotem, editors. *Scientific Data Management: Challenges, Technology, and Deployment*. Chapman & Hall/CRC Press, 2010.
- [23] K. Stockinger, E. W. Bethel, S. Campbell, E. Dart, , and K. Wu. Detecting Distributed Scans Using High-Performance Query-Driven Visualization. In SC. IEEE Computer Society Press, Nov. 2006.
- [24] K. Stockinger, J. Shalf, W. Bethel, and K. Wu. Query-driven visualization of large data sets. In *IEEE Visualization 2005, Minneapolis, MN, October 23-28, 2005*, page 22, 2005.
- [25] The HDF Group. HDF5 user guide. http://hdf.ncsa.uiuc.edu/HDF5/doc/H5.user. html, 2010.
- [26] T. Tu, H. Yu, et al. Remote runtime steering of integrated terascale simulation and visualization. In *SC HPC Analytics Challenge*, 2006.
- [27] Unidata. The NetCDF users' guide. http://www.unidata.ucar.edu/software/ netcdf/docs/netcdf/, 2010.
- [28] K. Wu, S. Ahern, et al. FastBit: Interactively searching massive data. In *SciDAC*, 2009.
- [29] T. Wu, J. Chou, N. Podhorszki, J. Gu, Y. Tian, S. Klasky, and K. Wu. Apply block index technique to scientific data analysis and i/o systems. In *IEEE/ACM International Workshop on Distributed Big Data Management (DBDM) at CCGrid*, May 2017.
- [30] T. Wu, H. Shyng, J. Chou, B. Dong, and K. Wu. Indexing blocks to reduce space and time requirements for searching large data files. In *2016 16th IEEE/ACM International Symposium on Cluster, Cloud and Grid Computing (CCGrid)*, pages 398–402, May 2016.

