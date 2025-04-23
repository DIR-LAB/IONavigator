# An End-to-end and Adaptive I/O Optimization Tool for Modern HPC Storage Systems

Bin Yang1 4 , Yanliang Zou2 4 , Weiguo Liu1 4 , Wei Xue3 4

1 School of Software, Shandong University

2 School of Information Science and Technology, ShanghaiTech University

3 Department of Computer Science and Technology, Tsinghua University

4 National Supercomputing Center in Wuxi

*Email: bin.yang@mail.sdu.edu.cn, zouyl@shanghaitech.edu.cn, weiguo.liu@sdu.edu.cn, xuewei@tsinghua.edu.cn*

*Abstract*—Real-world large-scale applications expose more and more pressures to storage services of modern supercomputers. Supercomputers have been introducing new storage devices and technologies to meet the performance requirements of various applications, leading to more complicated architectures. High I/O demand of applications and the complicated and shared storage architectures make the issues, such as unbalanced load, I/O interference, system parameter configuration error, and node performance degradation, more frequently observed. And it is challenging to both achieve high I/O performance on application level and efficiently utilize scarce storage resources.

We propose AIOT, an end-to-end and adaptive I/O optimization tool for HPC storage systems, which introduces effective I/O performance modeling and several active tuning strategies to improve both the I/O performance of applications and the utilization of storage resources. AIOT provides a global view of the whole storage system and searches for the optimal end-to-end I/O path through flow network modeling. Moreover, AIOT tunes system parameters across multiple layers of the storage system by using the automated identified application I/O behaviors and the instant status of the workload of storage system. We verified the effectiveness of AIOT for balancing I/O load, resolving I/O interference, improving I/O performance by configuring appropriate system parameters, and avoiding I/O performance degradation caused by abnormal nodes through quite a few realworld cases. AIOT has helped to save over ten millions of corehours during the deployment on Sunway TaihuLight since July 2021. It's worth mentioning that our proposed AIOT is capable of managing other I/O optimization methods across various storage platforms.

*Index Terms*—I/O modeling, auto-tuning, load imbalance, resource allocation, Sunway TaihuLight

#### I. INTRODUCTION

Large-scale scientific applications commonly produce large amounts of data, which stress the capabilities of the supercomputer's filesystem and storage system. New technologies and new storage media are adopted by cutting-edge HPC systems to meet the growing I/O demands, making the architecture of storage systems more complicated. Though the architecture increases the performance of storage systems, it also brings several severe issues. With these issues, applications running on supercomputers often suffer significant performance variability. And it also becomes more challenging to manage storage resources efficiently and improve the resource utilization of storage systems.

First, load imbalance has been identified as an important issue in many HPC storage systems [1]–[4]. With the architecture of storage systems becoming more and more complex, load imbalance has been uncovered at every layer, which makes resource management more difficult [5]–[7]. To resolve the problem, DFRA [8] tries to relieve load imbalance at the forwarding layer, while iez [9], TAPPIO [10] and BPIO [11] make efforts atop the back-end storage layer, such as Lustre [12], the widely-used parallel file system in HPC systems.

Second, I/O contention is also identified as an important cause for performance variability in HPC storage systems. Kuo et al. [13] study the interference from different file access patterns with synchronized time-slice profiles, while Yildiz et al. [14] focus on both software and hardware configurations. And several previous works [15]–[17] propose new scheduling strategies to relieve I/O interference among various HPC applications.

Third, recent studies prove that the system configurations can have impacts on both applications' performance and resource utilization [18], [19]. However, system configuration can be a massive challenge because of the increasing number of configurable parameters. Zhang et al. [20] use a Back Propagation (BP) neural network to auto-tune the configuration parameters. Wen et al. [21] use Reinforcement Learning instead of BP neural network to further improve the applications' performance atop Lustre.

Moreover, the fail-slow components can decrease applications performance as well. Gunawi et al. [22] firstly find the evidence for this phenomenon in large-scale production clusters. Ji et al. [8] demonstrate their claim on Sunway TaihuLight and try to avoid using the abnormal I/O nodes to server the coming jobs of applications.

Previous studies mainly focus on the single-layer optimizations to improve the I/O performance of applications and the utilization of storage resources, such as optimizations for the forwarding layer or the storage layer. The combination of single-layer optimizations may not achieve the best results for the current multi-layer storage systems. Moreover, The ever-changing I/O load in modern supercomputers places unprecedented demand on online optimization decisions with

1530-2075/22/$31.00 ©2022 IEEE DOI 10.1109/IPDPS53621.2022.00128 1294

accurate I/O behavior prediction, which have not been well addressed in previous works.

In this paper, we propose AIOT, an end-to-end and adaptive I/O performance optimization tool for modern supercomputers, which doesn't need any users' involvement. AIOT constructs an effective model to predict the I/O patterns of the upcoming job. With the help of both this model and the instant workload of a storage system, AIOT further coordinates the multiple layers' optimizations and chooses the best-effort I/O scheme per-job. Notice that AIOT has been built over an open and pluggable framework and a centralized optimization engine, which can be extended to manage new I/O optimization strategies across various storage platforms of supercomputers.

This paper reports our design, implementation, and deployment of AIOT on Sunway TaihuLight, the world's No.4 supercomputer [23]. The main contributions of this paper are:

- We pioneer an end-to-end tool for coordinating all components in the HPC I/O stack to optimize applications' I/O performance, increase storage system utilization, and simplify resource management for modern supercomputers.
- We present an effective I/O auto-tuning method for real-world multi-layer storage systems, which includes a model to predict the upcoming job's I/O pattern, and a best-effort job scheduling scheme according to both the I/O pattern and the real-time system work load.
- We implement and evaluate the effectiveness of AIOT on Sunway TaihuLight, currently the world's No.4 supercomputer. Results show that AIOT can both improve applications' performance and increase the usage of storage systems.

# II. BACKGROUND AND PROBLEMS

# *A. Overview of Platform*

![](_page_1_Figure_8.png)

#### Fig. 1. Architecture of Sunway TaihuLight

We first introduce the platform used in this paper, Sunway TaihuLight, which is currently the world's No.4 supercomputer with 40960 compute nodes and 10,649,600 cores. Its theoretical peak performance can be up to 125 PFlop/s. Here we focus on its storage system, Icefish. Figure 1 shows the current architecture of Sunway TaihuLight including Icefish. The parallel file system is Lustre, one of the world's most widely-used POSIX-compliant parallel file systems. Icefish is configured and deployed as three independent and non-overlapping file systems, Online1, Online2, and Online3. Online1 is the default used file system for regular users, which has 12 Lustre Object Storage Servers (OSSs) and 12 Lustre Object Storage Targets (OSTs). Online2 and Online3 are the reserved file systems for "VIP" users. There are 144 OSSs and 432 OSTs for Online2 back-end storage, and 4 OSSs and 12 OSTs for Online3 backend storage. The OSSs currently run the Lustre parallel file system version 2.10, 2.5, and 2.12 for Online1, Online2, and Online3, respectively.

A global-shared layer of 240 I/O forwarding nodes connects the compute nodes to the Lustre back-end storage. Each forwarding node provides a bandwidth of 2.5GB/s and plays a dual role as a Lightweight File System (LWFS) server to the compute nodes and a client to the Lustre back-end. Eighty forwarding nodes are used for daily service, while the other 160 nodes serve as backup. The compute nodes are statically mapped to the forwarding nodes with the mapping ratio of 512:1.

## *B. Issues*

![](_page_1_Figure_15.png)

Fig. 2. Back-end storage utilization of both Sunway TaihuLight and Titan

Many users often complain that their applications running on the HPC systems suffer poor I/O performance and significant performance variability. However, the utilization of the storage systems is surprisingly low. Figure 2 shows the backend storage utilization of both Sunway TaihuLight and Titan [24] supercomputers. The I/O throughput of OSTs less than 1% of the peak occupies about 60% of the operation time. And more than 70% of the time, the I/O throughput of all OSTs is less than 5% of the peak. So, significant challenges exist for approaching the peak or even the consistent performance at scale.

![](_page_1_Figure_18.png)

Fig. 3. Load imbalance on the forwarding nodes and the Lustre OSTs of Sunway TaihuLight

*1) Issue 1, load imbalance:* Default resource allocation tends to introduce load imbalance, which is one of the important causes of performance degradation and low utilization in HPC storage systems. To verify this, we analyze the historical data collected on Sunway TaihuLight with Beacon [1] to check the I/O load over time, as shown in Figure 3. We can find that not only forwarding nodes suffer from unbalanced loads but also the OSTs. However, most of the previous works [8], [9] only focus on balancing load at a certain layer, which may not work well for the multi-layer storage architecture of modern supercomputers.

![](_page_2_Figure_1.png)

(a) I/O performance of the example application (b) I/O load of one of the heavily loaded OSTs

#### Fig. 4. An example of I/O contention on the OST layer

*2) Issue 2, I/O interference:* I/O interference is also identified as an important issue for performance variability in HPC systems [25], [26], which is mainly contributed by I/O contention. Figure 4(a) shows an example of I/O performance degradation. The example application running on Sunway TaihuLight has the periodic I/O access with the same pattern and monopolizes a forwarding node. However, it still suffers significant performance interference. The reason is that several OSTs used by the application have ever experienced high load, and Figure 4(b) shows the I/O load of one of the heavily loaded OSTs. This result confirms the findings of Orcun et al. [14]. Resolving or relieving contention should also be considered from a multi-layer perspective since the modern supercomputers' architecture becomes more and more complex.

![](_page_2_Figure_5.png)

Fig. 5. Performance comparison with different striping strategies

*3) Issue 3, system misconfiguration:* Recent works [18], [20] have shown that the performance of HPC storage systems is partially dependent on the configuration parameters. Currently, these parameters are usually set with static values by an experienced administrator. Take the widely used filesystem, Lustre, as an example. To keep from slowing the overall system performance when creating and opening these files, most systems are configured to use a 1 MB stripe size and a stripe count of 1 or 4, meaning only few storage targets are used per file [1], [25], [27]. However, this limits the aggregate bandwidth [9]. Figure 5 shows the performance of an application running on Sunway TaihuLight with different striping strategies.The ratio between the best performance and the performance of the default setting is 1.45 : 1.

As the storage architecture becomes more and more complex, there are more and more adjustable configuration parameters, which may lead to complicated performance behaviors. As a result, it is more and more difficult to make a good choice only relying on the administrator's experience. Moreover, the best-effort choice for these configuration parameters should be determined according to both the I/O patterns of jobs and the storage system load when scheduling different job.

*4) Issue 4, performance degradation:* Gunawi et al. [22] has found evidence of performance degradation in the largescale production system, and Ji et al. [8] try to avoid allocating abnormal forwarding nodes for jobs running on Sunway TaihuLight. If I/O resources are allocated according to the default static scheduling policy, applications assigned to work through these slow nodes will suffer severe performance degradation. For modern supercomputers, the increasing number of components may exacerbate this kind of issue.

#### III. DESIGN AND IMPLEMENTATION OF AIOT

We have designed and implemented AIOT on Sunway TaihuLight based on Beacon [1], a real-time I/O performance monitoring tool. It is worth mentioning that our design can be extended for storage systems with a similar multi-layer architecture.

![](_page_2_Figure_13.png)

Fig. 6. Architecture of AIOT

As shown in Figure 6, AIOT has three primary components, including I/O behavior prediction, policy engine, and policy executor. The I/O behavior prediction module proposes a model for predicting the I/O behavior of each upcoming job. The policy engine module presents a model for optimally scheduling jobs in a multi-layer storage system with dynamic real-time load changes and formulates optimization strategies for each upcoming job. The policy executor module consists of a tuning server and a dynamic tuning library. The tuning server and the dynamic tuning library work together to remap the optimal I/O path for the upcoming job. Besides, the tuning server is also responsible for modifying the prefetch strategy on forwarding nodes while the tuning library handles other parameter optimization strategies.

#### *A. I/O behavior prediction*

Since thousands of jobs run on the supercomputer every day, it is difficult to identify candidates' I/O behavior for optimization from so many jobs. Most previous works mentioned above don't take the prediction of candidates' I/O behavior into account, while the others adopt LRU-based prediction models, such as DFRA [8]. DFRA judged the upcoming job's I/O behavior according to the last history, which can only achieve an accuracy of 39.5% with our real-world datasets. This section will introduce our prediction model, which can reach an accuracy of 90.6% with our real-world datasets collected by Beacon, which include 638,354 jobs in total. The job I/O behavior prediction module is mainly divided into two parts. The first is to merge jobs with similar I/O behavior and classify them by user name, job name, and parallelism. The second is to predict the upcoming job's I/O behavior and match the specific I/O model.

*1) Similar job classification:* As we all know, the supercomputer runs thousands of jobs every day, and each one is identified by a unique Jobid. It is difficult to predict the I/O behavior of the next job if we think all these jobs' I/O behavior as unique. Fortunately, many of these jobs running on supercomputers have similar I/O behavior [28], so we can reduce the difficulty of predicting the next job's I/O behavior by merging similar jobs.

However, it is not straightforward to identify jobs with similar behavior from the pool of executed jobs. Re-running the same job may lead to slightly different behavior. Job running with different inputs or configurations (e.g., number of nodes) may also have different behavior. Our strategy for identifying similar jobs is divided into two steps: The first is to extract data that can describe the I/O behavior of the job. The second is to compute the similarity based on the extracted data.

Extract job data On Sunway TaihuLight, Beacon gathers I/O operations from the whole I/O path and job metadata from the SLURM workload manager. For each job, raw data will be processed into 4D data, including time, node list, I/O basic metrics, detailed metrics. The node list represents the nodes occupied by the job in the entire I/O path, including compute nodes, forwarding nodes, storage nodes, and OSTs. I/O basic metrics represent the common I/O performance indicators [1] of the job, such as IOBW, IOPS, MDOPS, I/O parallelism, I/O mode, etc. Detailed metrics represent the job's detailed I/O behaviors, such as file access patterns, queue length in LWFS, OST striping setups in Lustre, etc.

![](_page_3_Figure_4.png)

Fig. 7. An example of clustering

Compute the similarity In order to compute the similarity of jobs, we classify these jobs into several categories based on user name, job name, and parallelism. After analyzing more than 630,000 jobs from December 2017 to July 2021, we find that 98% of the jobs can be classified into a number of categories. Each category has the same username, job name, and parallelism setups, while the rest 2% are single-run applications. Then, we use DWT (Discrete wavelet transform) [1] to extract I/O phases for each job in the same category. Each I/O performance indicator in I/O basic metrics, such as IOBW, is a waveform graph over a while. I/O phases represent the I/O behavior of a job in a continuous period, and a job may have several I/O phases. Besides, we use the DBSCAN cluster algorithm to find similar I/O phases through their I/O basic metrics and merge the jobs with similar I/O phases. Figure 7 shows an example of clustering I/O phases. There are three jobs in the category, and the red boxes mark I/O phases. I/O phases of Job B are different from the others. So, Job A and Job C are similar jobs. Then, we mark their I/O behavior with a numeric ID. In this example, (0, 1, 0) represents the I/O behavior of Job A, B, and C, respectively. Table I shows results, and numeric IDs of these jobs are sorted according to their submission time. The table's left column represents the names of all categories, and the right column represents the submission sequence. Among them, jobs with similar I/O behavior have the same numeric ID.

*2) I/O behavior prediction:* For each job submitted by users, the job scheduler will allocate resources to the job before it runs. During the period, AIOT obtains upcoming jobs' basic information (such as username, job name, parallelism, etc.) through an embedded dynamic library. The dynamic library mainly has two functions: Job start function and Job f inish function. First, the job scheduler calls the Job start function to transfer the job's I/O basic information to AIOT through the socket connection. Then, the job scheduler determines whether the job should continue to run based on the feedback from AIOT. When the job has finished, the job scheduler will let AIOT release the resources occupied by the job via the Job f inish function.

| TABLE I |
| --- |
| JOB SUBMISSION SEQUENCE |

| Category | Numeric ID sequence |
| --- | --- |
| user1 wrf 1024 | 001122211 |
| user2 cfd 256 | 001111111 |
| user1 wrf 256 | 001123444522 |
| ... | ... |
| usern md 2048 | 00001122233 |

For an upcoming job, we can classify it into one of the categories in Table I based on its basic information. That means we need to predict the I/O behavior of the job in a given category. We then transform the problem of predicting I/O behavior into a problem of predicting the next number based on a sequence of numbers.

Two kinds of models have been proposed to solve this problem: Markov chains (MC) models and Recurrent neural network (RNN) models. However, they all have some limitations. MC-based models can only capture short-term dependencies. They may ignore long-term dependencies because MC assumes that the current interaction only depends on one or a few recent interactions. By contrast, RNN based models need denser datasets to capture more complex dependencies in the sequence, but it is not suitable for some sparse datasets. To balance these two kinds of models, we introduce a selfattention mechanism. With the help of the self-attention mechanism, our model can have a different focus on different datasets. For sparse datasets, historical item information at a similar time is more critical because there are fewer user "activities". On the contrary, all historical user "activities" are essential for dense datasets. The principle of this model can be found in SASRec [29].

## *B. Policy engine*

The policy engine is the second important part of AIOT and is responsible for formulating appropriate optimization strategies for each upcoming job. To reduce the complexity of the problem, we divide the optimization strategy into two steps. The first step is to find the optimal I/O path. Its primary purpose is to allocate a relatively idle I/O path for the upcoming job to avoid performance interference and balance the load on different I/O paths as much as possible. At the same time, the policy engine also ensures that the I/O nodes on the specific I/O path can bear sufficient load, which makes the optimizations of the second step feasible. The second step is to adjust the system parameters to match various I/O behaviors. Its primary purpose is to make full use of allocated I/O nodes on the I/O path to improve both applications' performance and system utilization. It is worth mentioning that although we divide the whole optimization strategy into two steps, our optimization doesn't ignore the relationship between the two steps. The formulation of the optimization strategy fully considers the relationship between the two steps.

![](_page_4_Figure_3.png)

Fig. 8. The whole I/O path of a job running on N compute nodes

*1) Find the optimal I/O path:* Figure 8 shows the whole I/O path of a job, which is a directed graph. Taking one job running on Sunway TaihuLight as an example, the I/O load will cover several layers, including compute nodes, forwarding nodes, storage nodes, and disk arrays (disk arrays act as Lustre OSTs).

We introduce a flow network model to describe this directed graph. "Job start" refers to the ideal I/O load of a job and is the only source point S of the directed graph. The ideal load is determined by the job's I/O mode and maximum historical load. "Job end" refers to the final actual I/O load received and is the only convergence point T of the directed graph. (u, v) represents edges linking the layers in the graph, and their capacities can be expressed as c(u, v). c(u, v) is not static and must be dynamically adjusted according to the real-time I/O load. It is worth mentioning that due to the diverse I/O behaviors of the job, the representation of the I/O load is not a single indicator. For example, for the high IOBW I/O load, c(u,v) is constructed primarily by the I/O bandwidth. For the high IOPS I/O load, c(u,v) is constructed primarily by the IOPS. For the high MDOPS I/O load, c(u,v) is constructed primarily by the MDOPS [1]. So, we use Equation 1 to expressed c(u,v).

$$c(u,v)=(x_{1}Y_{1}+x_{2}Y_{2}+x_{3}Y_{3})*(1-U_{real})\tag{1}$$

Generally, Y1, Y2, and Y3 represent each node's historical peak IOBW, IOPS, and MDOPS, respectively. And, x1, x2 and x3 can be calculated through the equation x1Y1 = x2Y2 = x3Y3 (To simplify the calculation, x1 is set to 0.1). Especially for compute nodes, IOBW, IOPS, and MDOPS represent the ideal I/O load of the upcoming job. That means capacities of all edges from S to allocated compute nodes represent the I/O load of the upcoming job. Ureal represents the real-time load of each node. For compute nodes, Ureal is always 0 because each job exclusively occupies their allocated compute nodes, so the scheduled compute node must be in an idle state. For forwarding nodes, Ureal is determined by the real-time length of the request waiting queue. For storage nodes, Ureal is determined by the real-time I/O load of 3 linked OSTs. For OSTs, Ureal is determined by the real-time IOPS and IOBW. Each c(u, T) can be set to an infinite value for convergence point T because T is the abstraction of "Job end" and does not affect the final result.

Our goal is to find the maximum flow and allocate the I/O path for each upcoming job. And we hope that for each job, the I/O resources used should be as few as possible without wasting system resources. Generally speaking, the solution to the flow network is carried out by the method of finding an augmented path through DFS (Deep First Search ) or BFS (Breadth-first Search), such as FF (Ford–Fulkerson) and EK (Edmonds–Karp). For a directed graph G with V nodes and E edges, the time complexity of FF or EK is O(VE2 ). We design a new algorithm based on two special features in our scenario to reduce the time complexity and overhead. One is no reverse edge in graph G. The other is each augmentation path must pass through all layers. That means each augmentation path can be expressed as "S -> compute node -> Forwarding node -> Storage node -> OST -> T". So we can use a greedy approach to find the augmentation path. For each edge (S, Comp) linking the layers between the source point S and compute nodes, we choose edges with the largest capacity on the path from compute nodes to OSTs. In order to obtain the largest c(u,v) quickly, we maintained an ordered queue sorted by Ureal for each layer. Here we use bucket sorting and divide 6 buckets according to the value of Ureal (0, (0, 20%], (20%, 40%], (40%, 60%], (60%, 80%], (80%, 100%]). For each bucket, all c(u,v) that meet the conditions are stored in the form of a queue. It is worth mentioning that a queue Abqueue is used to store all performance degraded or abnormal I/O nodes, and these nodes will not be allocated for jobs.

Algorithm 1 shows the details. C(S, Comp) represents capacities of all edges (S, Comp) linking the layers between the source point S and compute nodes. C(Comp, Fwd) represents capacities of all edges (Comp, Fwd) linking the layers between compute nodes and forwarding nodes. Similarly, C(Fwd, SN) and C(SN, OST). The first step of the algorithm is initialization, establishing a directed graph G according to the monitoring system's data. Then, use bucket sorting to sort Ureal. Next, traverse the compute nodes and search the largest c(u,v) on each layer to construct the augmenting path S -> Compx -> F wdi -> SNj -> OSTk and compute the positive residual capacity d for the augmenting path. Finally, update c(comp, F wdi), c(F wd, SNj and c(SNj , OSTk) according to d. The time complexity of the optimized algorithm is O(E) + O(V).

![](_page_5_Figure_2.png)

Compared with previous works, such as DFRA [8], IEZ [9], AIOT extends the I/O path optimization to the entire I/O path of the storage system where the load changes in real-time. Besides, AIOT can allocate appropriate resources to jobs to improve I/O performance and reduce resource waste.

*2) Parameter optimization:* Incorrect system parameter configuration may also significantly impact jobs' performance. In order to understand the performance impact of system parameters for different application I/O behaviors, we deeply analyze data collected by Beacon on Sunway TaihuLight from December 2017 to July 2021 and find several system parameters that significantly impact on specific I/O behaviors. Adaptive prefetch strategy on forwarding nodes On Sunway TaihuLight, forwarding nodes play the role of LWFS server and Lustre client simultaneously. However, LWFS has no cache function and is mainly responsible for forwarding I/O requests. So, we adjust prefetch parameters on the Lustre client. Figure 9 shows two kinds of prefetch strategies. One shown on the left side is conservative. The other shown on the right side is aggressive. In the case of a conservative strategy, the prefetch buffer is divided into many chunks and is efficient for many small files. On the contrary, the aggressive strategy can perform well for several big files. Unfortunately, this configuration is rarely changed in HPC centers, and misconfiguration may bring some performance degradation, such as cache thrashing [1]. AIOT performs adaptive prefetch strategies to avoid this problem. For each upcoming job, AIOT uses Equation 2 to decide the prefetch strategy. *Prefetch buffer* represents the size of the prefetch buffer on forwarding nodes, *Fwds* represents the number of forwarding nodes allocated to the job, and *Read files* represents the number of files read by the job. If the job's primary read quest size is less than *Chunk size*, and I/O loads of forwarding nodes are light. Then, use *Chunk size* instead of the old parameter. Otherwise, do not change the strategy.

| 1 |  |  | 2 | 3 | 4 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Files |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | Prefetch buffer |
| 1-1 | 2-1 | 3-1 | 4-1 |  |  |  | 1 |  |  |  | 2 |  |  | 3 | 4 |
| 1-1 | 2-1 | 3-1 | 4-1 |  |  |  |  |  |  |  |  |  |  |  |  |
| 1-2 | 2-2 | 3-2 | 4-2 |  |  |  | 5 |  |  |  | 6 |  |  | 7 | 8 |
| 1-2 | 2-2 | 3-2 | 4-2 |  |  |  |  |  |  |  |  |  |  |  |  |

Fig. 9. Examples of incorrect prefetch strategy settings

$$Chunk\_size=\frac{Prefetch\_buffer*Fwds}{Read\_files}\tag{2}$$

Adaptive request scheduling on forwarding nodes The default I/O request scheduling strategy on the LWFS server is that metadata operations have the highest priority. However, a recent study demonstrates that this strategy may bring serious interference between applications [8]. One way to solve this problem is isolating applications to different forwarding nodes. But there is a prerequisite that there are enough idle forwarding nodes. In order to relieve interference when lacking idle forwarding nodes, we set a dynamic request scheduling strategy for the LWFS server based on jobs' I/O behaviors. For an upcoming job with high MDOPS, if it has to share forwarding nodes with other jobs, then we will change the default strategy. Instead of always giving metadata requests high priority, metadata and non-metadata requests follow a P : (1−P) ( P configurable ) split served by the LWFS server. Adaptive file striping on OSTs Generally, users rarely modify the default Lustre striping strategy [30]. Figure 10 shows examples of wrong OST striping strategies. Four processes share a 16MB file. For figure 10(a), process 1 operates the file from offset 0 to 4MB while process 2 operates the file from offset 4MB to 8MB. The remaining processes 3 and 4 use the remaining parts of the file. The 1MB Stripe size strategy results in these 4 processes accessing the OSTs serially and limits the aggregate bandwidth. Figure 10(b) shows a different strategy. Process 1 operates the file from offset 0 to 1MB, 4MB to 5MB, 8MB to 9MB, and 12MB to 13MB. Others stagger the access of files according to the size of 1MB. However, these 4 processes will also sequentially access OST1, OST2, OST3, and OST4 with Stripe size=4MB. AIOT performs an adaptive striping strategy according to file access patterns. For shared files, the striping strategy should be set according to the I/O bandwidth of a single process/OST, offset differences, and I/O parallelism, as Equation 3 shows. However, it is best to use no striping for exclusive files to avoid OST contention when dealing with a large number of files.

![](_page_6_Figure_1.png)

Fig. 10. Examples of OST striping strategy where Stripe count=4

$Stripe\_count=\dfrac{Process\_IOBW*IO\_parallelism}{OST\_IOBW}$ (3)
$Stripe\_size=\dfrac{Offset\_difference}{IO\_parallelism}$

![](_page_6_Figure_4.png)

Adaptive DoM on MDTs Data on Metadata Target (DoM) is a new feature of Lustre and can improve small files' performance. Users can use the command *lfs setstripe -E xMB -L mdt* to create a file with DoM layout. xMB represents put up to x MB data of the file on MDT. Unfortunately, few HPC centers can make good use of this feature. First, most users are not storage experts and may not be familiar with Lustre's commands. Besides, it will be very troublesome to set DoM for lots of files. Last but not least, the space of MDT is limited, and the load will change in real-time. So, whether to use the DoM must consider the real-time state of MDTs. AIOT proposes an adaptive DoM method. If the real-time I/O load of MDTs is light and MDTs have sufficient capacity, AIOT will try to set a file with DoM layout based on its historical metadata operands and file size. Also, files on MDT will be set with an expiration time and moved to OSTs for storage when not used for a long time.

#### *C. Policy executor*

The policy executor is divided into two parts. One is a tuning server deployed on the AIOT engine server for performing strategies that need to be set before the job runs. The other is a dynamic tuning library embedded in an LWFS server for performing runtime strategies.

*1) Tuning server:* The tuning server tries to conduct two optimizations according to the determined job policy, including remapping compute nodes to forwarding nodes and modifying prefetch strategies on Luster clients. When the tuning server receives the optimization strategies for the upcoming job from the policy engine via RPC, it will execute them in turn. If necessary, the tuning server will fork up to 256 threads to execute concurrently. When all optimization strategies have been executed, the tuning server will send feedback to the policy engine. Then, the policy engine will forward the feedback to the dynamic library embedded in the job scheduler.

|  | Algorithm 2 Primary functions of the dynamic tuning library |
| --- | --- |
|  | Input: Strategies of the upcoming jobs |
|  | Output: Results of strategies execution |
|  | 1: procedure AIOT SCHEDULE |
| 2: | Sync fetch and add(&op, 1); |
| 3: | if (op == TIME LIMIT) then |
| 4: | P = read parameter() |
| 5: | Sync fetch and and(&op, 0); |
| 6: | end if |
| 7: | if (rand() < p) then |
| 8: | server rw requst(); |
| 9: | else |
| 10: | server md request(); |
| 11: | end if |
|  | 12: end procedure |
|  | 13: procedure AIOT CREATE(pathname, flags, mode) |
| 14: | strategy, f lag = read strategy(pathname); |
| 15: | if (flag == None) then |
| 16: | f d = open(pathname, f lags, modes); |
| 17: | return f d; |
| 18: | end if |
| 19: | f lags = f lags|O NONBLOCK; |
| 20: | head = llapi layout alloc(); |
| 21: | if (flag == DoM) then |
| 22: | llapi layout pattern set(head, DOM); |
| 23: | llapi layout strategy set(head, strategy); |
| 24: | else |
| 25: | llapi layout pattern set(head, OST); |
| 26: | llapi layout strategy set(head, strategy); |
| 27: | end if |
| 28: | f d = llapi layout f ile open(real path, |
|  | f lags, mode, head); |
| 29: return f d; |  |
| 30: end procedure |  |

*2) Dynamic tuning library:* The dynamic tuning library handles the remaining optimization strategies, including two primary functions as shown in Algorithm 2. One is responsible for modifying the request scheduling strategy on the LWFS server according to the parameter set by the policy engine. In order to reduce the overhead, the function will check the current parameter according to the configurable time interval. The other is responsible for allocating I/O node resources (storage nodes, OSTs) and setting data layout strategies (OST striping, DoM) for the upcoming jobs.

#### *D. Generality*

AIOT can work well with other multi-layer monitoring tools like Beacon. In addition, (1) with job-level monitoring tools like Darshan [31], AIOT can provide the job I/O behavior prediction for developers and users to make code improvements and configuration adjustments, such as Lustre striping; (2) with back-end load monitoring tools like LMT [32], AIOT can help to find the optimal I/O path and tune Lustre configuration automatically for both better load balance and better utilization of back-end storage; (3) without any I/O monitoring tools, AIOT can also help to simplify the implementation of userdefined optimization strategies, such as setting striping for lots of files.

#### IV. EVALUATION

#### *A. Job Statistics from I/O History Analysis*

First, AIOT relies on the applications' overall consistency in I/O behavior. We verified this with the 43-month Sunway TaihuLight I/O profiling results, confirming observations by existing studies [16], [25]. To help formulate suitable optimization strategies, AIOT forecasts the upcoming job's I/O behavior with a self-attention-based method. Compared to the LRU model used by DFRA (forecast the next job's I/O behavior by using its latest run with the same number of compute nodes), AIOT successfully increase the accuracy of the prediction from less than 40% to 90.6% with under 20% deviation for 638, 354 jobs in total.

TABLE II JOBS STATISTICS BENEFITING FROM AIOT WITH REPLAYING HISTORICAL DATA

| Category | Count | Count(%) | Core-hour(%) |
| --- | --- | --- | --- |
| Total jobs | 638, 354 | 100 | 100 |
| Job benefits | 199, 575 | 31.2% | 61.7% |

We then give statistics about AIOT's decisions and potential beneficiaries by replaying these 43-month jobs I/O profiles from December 2017 to July 2021. Table II lists the results. 31.2% jobs are granted upgrades and expected to benefit from AIOT, and these jobs consume more than 60% corehours. This result demonstrates that many jobs are potential beneficiaries with AIOT. However, there are still some jobs that cannot benefit from AIOT even after correct prediction. The following are some reasons: (1) jobs that have light I/O workloads and are not disturbed across the I/O path (the most observed scenarios); (2) jobs with totally random access to a shared file, which currently cannot be handled well using AIOT.

#### *B. Load imbalance improvement*

AIOT ensures load balance through dynamically allocating lightly loaded I/O nodes for jobs. And the I/O nodes in the same bucket follow the principle of queues, and no node will starve (Under certain conditions, a certain group of I/O nodes will always provide services while others are idle for a long time.) To evaluate AIOT's effectiveness on relieving load imbalance over all layers, we replay a 3-day historical data collected by Beacon and compare the load of each layer with or without AIOT. Figure 11 shows the results. The load balancing index refers to the standard deviation of nodes' load at each layer and is mapped to [0, 1]. As we can see, AIOT can effectively balance the load of nodes at each layer.

![](_page_7_Figure_10.png)

Fig. 11. Load balance comparison w/o AIOT

#### *C. I/O interference migration*

*1) Isolating I/O resources:* In order to evaluate AIOT's effectiveness in resolving I/O interference, we conduct a test in a relatively small testbed, including 2048 compute nodes, 4 forwarding nodes, and 4 storage nodes. Each forwarding node serves 512 compute nodes by default, and each storage node controls 3 OSTS. At the same time, two OSTs (OST1, OST2) controlled by the storage node SN1 are set to be busy and abnormal, respectively. First, several applications are submitted without AIOT, and details of these applications are as follow:

- XCFD [33] is a computational fluid dynamics application with N-N I/O mode and high I/O bandwidth. By default, It is allocated to compute nodes Comp1 - Comp512 and monopolizes a forwarding node F wd1.
- Macdrp [34] is a high I/O bandwidth seismic simulation application with N-N I/O mode. It is allocated to compute nodes Comp513 - Comp768 and monopolizes a forwarding node F wd2.
- Quantum [35] is a high MDOPS quantum simulation application with many metadata operations. It is allocated to compute nodes Comp769 - Comp1280 and shares a forwarding node F wd2 with Macdrp.
- WRF [36] is a forecasting model with 1-1 I/O mode and low I/O bandwidth. It is allocated compute node Comp1281 - Comp1536 and shares a forwarding node F wd3 with Quantum.
- Grapes [37] is a global/regional assimilation and prediction enhanced system with N-1 I/O mode. It is allocated compute nodes Comp1537 - Comp2048 and monopolizes a forwarding node F wd4.

Then, we re-submit these applications with AIOT, and results are shown in Table III. XCFD and Grapes each monopolize a forwarding node in the default configuration but still experience significant performance degradation because OST1 and OST2 are in their I/O path. Macdrp, Quantum, and WRF have serious interference on the forwarding nodes, so the performance degradation is also pronounced. After AIOT tuning, the performance of all applications returns to normal as these applications are isolated on the forwarding nodes, storage nodes, and OSTs. At the same time, AIOT avoids assigning OST1 and OST2 to applications.

TABLE III PERFORMANCE COMPARISON W/O AIOT

| Application | Base performance | Without AIOT | With AIOT |
| --- | --- | --- | --- |
| XCFD | 1.0 | 4.8 | 1.0 |
| Macdrp | 1.0 | 5.2 | 1.0 |
| Quantum | 1.0 | 1.3 | 1.0 |
| Wrf | 1.0 | 24.1 | 1.0 |
| Grapes | 1.0 | 3.1 | 1.0 |

![](_page_8_Figure_3.png)

Fig. 12. Performance comparison w/o the scheduling strategy adjustment

*2) Adjust scheduling strategy on forwarding nodes:* For I/O interference caused by high MDOPS applications on the forwarding nodes, it is also possible to relieve I/O interference by adjusting the scheduling strategy of the LWFS server. And, it is necessary for scenarios with limited I/O forwarding nodes. Figure 12 shows an example of two applications sharing the same forwarding node. As we can see, Macdrp's performance improves about 2X while Quantum only perceives a 5% slowdown after AIOT adjustment.

#### *D. System parameters re-configuration*

This section evaluates AIOT's effectiveness for improving applications' performance by adjusting system configuration parameters.

![](_page_8_Figure_8.png)

Fig. 13. Performance improvements of adjusting read prefetch strategy

*1) Evaluation on adaptive prefetch strategy:* Figure 13 shows the performance comparison of Macdrp running on 256 nodes without using AIOT, using AIOT, and modifying the source code. In the case of the default configuration, the performance of compute nodes is much lower than that of forwarding nodes which indicates that the prefetch buffer of the forwarding node is not effectively used. The prefetch strategy of the forwarding node is aggressive, and a lot of data in the buffer is discarded. AIOT improves the performance by reducing the Chunk size of the prefetching buffer. Compared with modifying the source code, it is more convenient.

*2) Evaluation on adaptive file striping:* We take Grapes as an example to demonstrate that AIOT can dynamically set appropriate striping strategies for applications. Grapes runs with 256 processes, and 64 processes are selected to write a shared file with MPI-IO. Figure 14 shows the results. All 64 I/O processes write to the same OST in the default layout, limiting scalability. AIOT re-sets Lustre OST striping configuration according to Grapes's I/O behavior and improves performance by about 10% on average.

![](_page_8_Figure_12.png)

Fig. 14. Performance improvements of re-setting OST striping strategies

![](_page_8_Figure_14.png)

(a) DOM test on Sunway TaihuLight (b) Performance of FlameD

Fig. 15. Performance improvements of adaptive DoM

*3) Evaluation on adaptive DoM:* We first tested the impact of Lustre DoM on small files' read performance on Sunway Taihulight. Figure 15(a) shows the results of the test, where file size represents the sizes of different small files. After adopting the DoM, small files' read performance can be improved by about 15%, which means DoM may be helpful for some applications that frequently read small files. Then, we take FlameD [38], an application for engine fuel combustion simulation, as an example. FlameD frequently operates small files and its I/O time accounted for more than 50 % of the total running time. Figure 15(b) shows the performance comparison before and after optimization, and the overall improvement for the application is about 6%. It is worth noting that since the Lustre MDS on Sunway TaihuLight is not equipped with SSDs, performance optimization of DoM for small files isn't particularly obvious. However, in some environments with MDS configured with SSDs, AIOT can achieve higher performance.

#### *E. Overhead*

Since the prediction module and the policy engine module only take under 0.1s in all tests on Sunway TaihuLight, we primarily assess the overhead of the policy executor module. For the tuning server, node remapping occupies the main overhead as modifying prefetch and request scheduling strategy on all forwarding nodes only takes up to 0.2s. Figure 16 shows the maximum time cost (including all optimizations) for different parallelism, plus the corresponding job dispatch time (without AIOT) as reference. The tuning server overhead is linear growth when more compute nodes are involved, but it composes a minor addition to the baseline job dispatch time. Note that such minor delay in job dispatch is negligible compared with the total time saved, especially for long-running jobs. Generally speaking, for some regular applications, AIOT can help save a few minutes of running time, and for some longterm applications, AIOT can help save hours of running time.

![](_page_9_Figure_1.png)

Fig. 16. Overhead of the tuning server

![](_page_9_Figure_3.png)

Fig. 17. Overhead of function AIOT CREATE

For the dynamic tuning library, the overhead is composed of two functions. Compared to the overhead of function AIOT CREATE, function AIOT SCHEDULE almost has no impact on I/O request performance in our tests. So here, we only show the overhead of function AIOT CREATE. Figure 17 shows the change in execution time of each create I/O request on the LWFS server (have no impact on other I/O operations, such as operating an existing file), and the average overhead is less than 1%.

## V. RELATED WORK

Load imbalance DFRA [8] focuses on the forwarding layers architecture of HPC systems and tries to relieve load imbalance by changing the static map to the dynamic map while other works focus on the back-end storage [11], [39]–[41]. These works tend to change the default storage servers allocations (Lustre OSTs) by intercepting applications' I/O operations. Nevertheless, the lack of servers' real-time load makes this optimization method highly dependent on the environment. Other efforts extend the above approach to more efficiently allocate OSTs to applications by capturing load information for all storage servers [2], [9].

However, these existing approaches lack a global view of all the components in the system's hierarchical structure and instead focus on a specific layer of the hierarchical structure. I/O interference Two kinds of methods have been proposed to resolve or relieve the I/O interference. One method is scheduling from the application level, which relieves interference by scheduling applications. AID [25] identifies applications' I/O patterns and reschedules heavy I/O applications to avoid interference. CALCioM [15] coordinates applications' I/O activities dynamically via inter-application communication. Gainaru et al. [16] analyze the impact of congestion on applications' I/O bandwidth. The other is system-level scheduling, which relieves interference by scheduling system resources. Neuwirth et al. [42] use a OST scheduling strategy proposed by BPIO [11] to extend the functionality of ADIOS [43]. Qian et al. [44] present a token bucket filter in Lustre to guarantee QoS under interference.

Our work combines application-level scheduling with system-level scheduling and complements the above studies. System misconfiguration Recent works [18], [20] demonstrate that the performance of HPC storage systems is partially dependent on configuration parameters. At present, these parameters are set with static values or by experienced administrator [27] Fan et al. [20] try to use a back propagation neural network for autotuning of the configuration parameters. Haifeng et al. [45] introduce deep learning and test it on a server node while Wentao et al. [21] and Yan et al. [46] introduce Reinforcement Learning for cluster systems.

Though machine learning or deep learning can achieve good performance on their data sets, they still lack analytical models that incorporate the actual physical implications to anticipate the effect of a change.

Performance degradation of system nodes The performance degradation of system nodes has been unnoticed for a long time because it was difficult to detect. However, as more and more advanced monitoring systems are deployed in HPC, performance degradation of nodes is increasingly concerned [22]. Ji et al. [8] avoided using forwarding nodes with abnormal performance through DFRA. Our work extends the above work and avoids all abnormal nodes on the I/O path.

#### VI. CONCLUSION

In this work, we present the design and implementation of AIOT, an end-to-end and adaptive performance optimization tool, to improve the I/O performance of HPC applications and the utilization of modern HPC storage systems with multilayer architecture. This tool has been deployed on the current No. 4 supercomputer, Sunway TaihuLight, since July 2021 and manages to save over 10 millions of core-hours. Our experience of deploying and evaluating with many real-world applications demonstrates the effectiveness of AIOT for balancing load, resolving I/O interference, improving performance by configuring appropriate system parameters, and avoiding performance degradation due to using abnormal nodes. Moreover, our proposed AIOT is both portable and extensible, which is capable of managing other I/O optimization methods across various storage platforms.

#### ACKNOWLEDGMENT

We appreciate the thorough and constructive comments from all reviewers. We thank Prof. Shu Yin for his valuable guidance, Mr. Mingshan Shao and Mr. Shichao Liu for their contributions to Beacon, and Mr. Wanliang Li and Mr. Hao Zou for great support to this work. This work is partially supported by the National Key R&D Program of China (Grant No.2017YFC1502203), National Natural Science Foundation of China (Grant No.U1806205 and 61972231), the Key Project of Joint Fund of Shandong Province (Grant No.ZR2019LZH007), and Engineering Research Center of Digital Media Technology, Ministry of Education, China. The corresponding author is Wei Xue(xuewei@tsinghua.edu.cn).

#### REFERENCES

- [1] B. Yang, X. Ji, X. Ma, X. Wang, T. Zhang *et al.*, "End-to-end i/o monitoring on a leading supercomputer," in *16th USENIX Symposium on Networked Systems Design and Implementation*, 2019.
- [2] A. K. Paul, A. Goyal, F. Wang, S. Oral, A. R. Butt, M. J. Brim, and S. B. Srinivasa, "I/o load balancing for big data hpc applications," in *2017 IEEE International Conference on Big Data*. IEEE, 2017.
- [3] E. Meneses, L. V. Kale, and G. Bronevetsky, "Dynamic load balance for optimized message logging in fault tolerant hpc applications," in *2011 IEEE International Conference on Cluster Computing*. IEEE, 2011.
- [4] D. Clarke, A. Lastovetsky, and V. Rychkov, "Dynamic load balancing of parallel computational iterative routines on highly heterogeneous hpc platforms," *Parallel Processing Letters*, 2011.
- [5] D. H. Ahn, J. Garlick, M. Grondona *et al.*, "Flux: A next-generation resource management framework for large hpc centers," in *2014 International Conference on Parallel Processing Workshops*. IEEE, 2014.
- [6] S. E. Niewiadomska and P. Arabas, "Resource management system for hpc computing," in *Conference on Automation*. Springer, 2018.
- [7] W. Fox, D. Ghoshal, A. Souza *et al.*, "E-hpc: a library for elastic resource management in hpc environments," in *Proceedings of the 12th Workshop on Workflows in Support of Large-Scale Science*, 2017.
- [8] X. Ji, B. Yang, T. Zhang, X. Ma, X. Zhu *et al.*, "Automatic, applicationaware i/o forwarding resource allocation," in *17th USENIX Conference on File and Storage Technologies*, 2019, pp. 265–279.
- [9] B. Wadhwa, A. K. Paul *et al.*, "iez: Resource contention aware load balancing for large-scale parallel file systems," in *2019 IEEE International Parallel and Distributed Processing Symposium*. IEEE, 2019.
- [10] S. Neuwirth, F. Wang, S. Oral, and U. Bruening, "Automatic and transparent resource contention mitigation for improving large-scale parallel file system performance," in *Proc. IPDPS*. IEEE, 2017.
- [11] F. Wang, S. Oral *et al.*, "Improving large-scale storage system performance via topology-aware and balanced data placement," in *Proc. IPDPS*. IEEE, 2014.
- [12] P. Braam, "The lustre storage architecture," *arXiv preprint arXiv:1903.01955*, 2019.
- [13] C.-S. Kuo, A. Shah, A. Nomura *et al.*, "How file access patterns influence interference among cluster applications," in *2014 IEEE International Conference on Cluster Computing*. IEEE, 2014.
- [14] O. Yildiz, M. Dorier, S. Ibrahim, R. Ross, and G. Antoniu, "On the root causes of cross-application i/o interference in hpc storage systems," in *2016 IEEE International Parallel and Distributed Processing Symposium*. IEEE, 2016.
- [15] M. Dorier, G. Antoniu, R. Ross, D. Kimpe, and S. Ibrahim, "Calciom: Mitigating i/o interference in hpc systems through cross-application coordination," in *2014 IEEE International Parallel and Distributed Processing Symposium*. IEEE, 2014.
- [16] A. Gainaru, G. Aupy, A. Benoit, F. Cappello, Y. Robert, and M. Snir, "Scheduling the i/o of hpc applications under congestion," in *Proc. IPDPS*. IEEE, 2015.
- [17] Z. Zhou, X. Yang, D. Zhao, P. Rich, W. Tang, J. Wang, and Z. Lan, "I/o-aware batch scheduling for petascale computing systems," in *2015 IEEE International Conference on Cluster Computing*. IEEE, 2015.
- [18] J. Han, D. Kim, and H. Eom, "Improving the performance of lustre file system in hpc environments," in *2016 IEEE 1st International Workshops on Foundations and Applications of Self Systems*. IEEE, 2016.

- [19] G. K. Lockwood, K. Lozinskiy, L. Gerhardt, R. Cheema *et al.*, "Designing an all-flash lustre file system for the 2020 nersc perlmutter system," *Proceedings of the 2019 Cray User Group*, 2019.
- [20] F. Zhang, J. Cao, L. Liu, and C. Wu, "Performance improvement of distributed systems by autotuning of the configuration parameters," *Tsinghua Science and Technology*, pp. 440–448, 2011.
- [21] Z. Wentao, W. Lu, and C. Yaodong, "Performance optimization of lustre file system based on reinforcement learning," *Journal of Computer Research and Development*, 2019.
- [22] H. S. Gunawi, R. O. Suminto, R. Sears, C. Golliher, *et al.*, "Fail-slow at scale: Evidence of hardware performance faults in large production systems," *ACM Transactions on Storage*, 2018.
- [23] H. Fu, J. Liao, J. Yang *et al.*, "The sunway taihulight supercomputer: system and applications," *Science China Information Sciences*, 2016.
- [24] "Titan Supercomputer," https://www.top500.org/system/177975/.
- [25] Y. Liu, R. Gunasekaran, X. Ma, and S. S. Vazhkudai, "Server-side log data analytics for i/o workload characterization and coordination on large shared storage systems," in *Proc. SC'16*. IEEE, 2016.
- [26] J. Ouyang, B. Kocoloski, J. R. Lange, and K. Pedretti, "Achieving performance isolation with lightweight co-kernels," in *Proc. IPDPS*. IEEE, 2015.
- [27] J. Lofstead, I. Jimenez, C. Maltzahn, Q. Koziol, J. Bent, and E. Barton, "Daos and friends: a proposal for an exascale storage system," in *Proc. SC'16*. IEEE, 2016.
- [28] E. Betke and J. Kunkel, "Classifying temporal characteristics of job i/o using machine learning techniques," *Journal of High Performance Computing*, vol. 1, 2021.
- [29] W.-C. Kang and J. McAuley, "Self-attentive sequential recommendation," in *2018 IEEE International Conference on Data Mining*. IEEE, 2018, pp. 197–206.
- [30] S.-H. Lim, H. Sim, R. Gunasekaran, and S. S. Vazhkudai, "Scientific user behavior and data-sharing trends in a petascale file system," in *Proc. SC'17*. IEEE, 2017.
- [31] P. Carns, R. Latham, R. Ross *et al.*, "24/7 characterization of petascale i/o workloads," in *International Conference on Cluster Computing and Workshops*. IEEE, 2009.
- [32] J. Garlick, "Lustre monitoring tool," 2010, https://github.com/LLNL/lmt.
- [33] J. D. Anderson and J. Wendt, *Computational fluid dynamics*. Springer, 1995, vol. 206.
- [34] B. Chen, H. Fu, Y. Wei, C. He, W. Zhang, Y. Li *et al.*, "Simulating the wenchuan earthquake with accurate surface topography on sunway taihulight," in *Proc. SC'18*. IEEE, 2018.
- [35] I. Buluta and F. Nori, "Quantum simulators," *Science*, 2009.
- [36] "A description of the advanced research WRF version 3," http://www2.mmm.ucar.edu/wrf/users/.
- [37] R. Zhang and X. Shen, "On the development of the grapes—a new generation of the national operational nwp system in china," *Chinese Science Bulletin*, vol. 53, no. 22, pp. 3429–3432, 2008.
- [38] "FLAMES," https://www.ternion.com/flames-overview/.
- [39] X. Li, L. Xiao, M. Qiu, B. Dong, and L. Ruan, "Enabling dynamic file i/o path selection at runtime for parallel file system," *The Journal of Supercomputing*, vol. 68, no. 2, pp. 996–1021, 2014.
- [40] Y. Tsujita, T. Yoshizaki, K. Yamamoto *et al.*, "Alleviating i/o interference through workload-aware striping and load-balancing on parallel file systems," in *International Supercomputing Conference*. Springer, 2017.
- [41] N. Zhao, A. Anware, Y. Cheng, M. Salman, D. Li, J. Wan, C. Xie, X. He, F. Wang, and A. Butt, "Chameleon: An adaptive wear balancer for flash clusters," in *Proc. IPDPS*. IEEE, 2018.
- [42] S. Neuwirth, F. Wang, S. Oral, S. Vazhkudai, J. Rogers, and U. Bruening, "Using balanced data placement to address i/o contention in production environments," in *Proc. SBAC-PAD*. IEEE, 2016.
- [43] J. Lofstead, N. Podhorszki, S. Klasky, C. Jin, and K. Schwan, "Flexible io and integration for scientific codes through the adaptable," in IO *System (ADIOS).", CLADE 2008 at HPDC*. Citeseer, 2008.
- [44] Y. Qian, X. Li, S. Ihara, L. Zeng, J. Kaiser, T. Suß, and A. Brinkmann, ¨ "A configurable rule based classful token bucket filter network request scheduler for the lustre file system," in *Proc. SC'17*, 2017.
- [45] H. Chen, G. Jiang, H. Zhang, and K. Yoshihira, "Boosting the performance of computing systems through adaptive configuration tuning," in *Proceedings of the 2009 ACM symposium on Applied Computing*, 2009.
- [46] Y. Li, K. Chang, O. Bel, E. L. Miller, and D. D. Long, "Capes: Unsupervised storage performance tuning using neural network-based deep reinforcement learning," in *Proc. Sc'17*, 2017.

