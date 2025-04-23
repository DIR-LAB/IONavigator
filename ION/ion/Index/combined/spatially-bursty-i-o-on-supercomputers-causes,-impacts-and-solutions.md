# Spatially Bursty I/O on Supercomputers: Causes, Impacts and Solutions

Jie Yu , Wenxiang Yang , Fang Wang, Dezun Dong , Jinghua Feng, and Yuqi Li

Abstract—Understanding the I/O characteristics of supercomputers is crucial for grasping accurate I/O workloads and uncovering potential I/O inefficiency. We collect and analyze I/O traces from two production supercomputers, and find that the I/O traffic peaks in the system not only occur in short periods of time but also originate from a minority of adjacent compute nodes, which we call spatially bursty I/O. Since modern supercomputers widely adopt I/O forwarding architecture, in which an I/O node performs I/O on behalf of a subset of compute nodes in the vicinity, spatially bursty I/O will cause significant load imbalance and underutilization on the I/O nodes. To address such problems, we quantitatively analyze the two causes of spatially bursty I/O, including uneven I/O distribution on job's processes and uneven job nodes distribution on the system. Two different solutions are proposed to mobilize more I/O nodes to participate in job's I/O activity. (1) We change the I/O node mapping, making adjacent compute nodes use different I/O nodes instead of a same one. (2) According to the job's I/O characteristics extracted from history I/O traces, we distribute the compute nodes of dataintensive jobs more sparsely to utilize more I/O nodes. Extensive evaluations of both solutions show that they can further exploit the potential of I/O forwarding layer. We have deployed the proposed I/O node mapping on a production supercomputer for 11 months. Our experience finds that it can effectively promote I/O performance, balance loads, and alleviate I/O interference.

Ç

Index Terms—Parallel I/O, bursty I/O, I/O forwarding, I/O node mapping, resource allocation

# 1 INTRODUCTION

AS THE fourth science paradigm, data-driven scientific discovery has powered numerous scientific breakthroughs by enabling researchers to manipulate and explore massive datasets [1]. However, researchers have realized that in many circumstances the ability to retrieve valuable knowledge from the datasets falls far behind the exponential growth rate of data [2], [3]. High performance computing (HPC) systems, the primary platform to conduct dataintensive scientific computing, also face the problem of insufficient I/O bandwidth for supporting the analysis on tremendous amounts of data. The mismatch between I/O and compute capability remains a challenging factor in determining the overall performance of extreme-scale systems.

Comprehensive studies have been conducted to understand the system I/O behaviors to promote the efficiency of the I/O system [4], [5], [6]. Researchers discovered a typical

- Jie Yu and Fang Wang are with the Computational Aerodynamics Institute, China Aerodynamics Research and Development Center, Mianyang 621000, China. E-mail: yujie@nudt.edu.cn, wangfangcardc@163.com.
- Wenxiang Yang is with the College of Computer, National University of Defense Technology, Changsha 410073, China and also with the Computational Aerodynamics Institute, China Aerodynamics Research and Development Center, Mianyang 621000, China. E-mail: yangwenxiang10@nudt.edu.cn.
- Dezun Dong is with the College of Computer, National University of Defense Technology, Changsha 410073, China. E-mail: dong@nudt.edu.cn.
- Jinghua Feng and Yuqi Li are with the National Supercomputer Centre in Tianjin, Tianjin 300457, China. E-mail: {fengjh, liyq}@nscc-tj.cn.

Manuscript received 13 Sept. 2019; revised 7 June 2020; accepted 19 June 2020. Date of publication 29 June 2020; date of current version 9 July 2020. (Corresponding author: Fang Wang.)

Recommended for acceptance by C. Ding.

Digital Object Identifier no. 10.1109/TPDS.2020.3005572

I/O behavior called bursty I/O on many different HPC facilities [7], [8], [9], [10], [11], which is a phenomenon that the enormous amount of system I/O traffic always arrives in short periods of time. Take a leadership system Intrepid as an example. Its I/O bandwidth is below 33 percent of its peak performance for 99.2 percent of the time [12]. Bursty I/O is often caused by application's transformation from compute-intensive stage to I/O-intensive stage, such as writing checkpoints, outputting results, etc. Much work [13], [14], [15], [16] has been devoted to redesigning the I/O stack because of bursty I/O since it leads to severe I/O inefficiency by making the storage system handle I/O traffic beyond its capability. In this paper, we further find that the I/O is not only bursty in the time dimension but also bursty in the space dimension, which we call spatially bursty I/O.

We collect the I/O traces from two production HPC systems, Tianhe-1A and CS19, and conduct comprehensive analyses. The results show that the short-duration I/O traffic peaks come only from a minority of compute nodes located close to each other. There are two main causes of spatially bursty I/O. First, jobs utilize many compute nodes to equally share the computing tasks, but the I/O workload often varies among different nodes. It leads to spatially bursty I/O when most of the I/O traffic concentrates on small numbers of compute nodes. Second, since the I/O of every job is bursty in time, there are probably only a few jobs performing I/O at the same time. Job scheduling systems like Slurm preferentially map jobs to adjacent compute nodes to minimize the communication overheads. Therefore, the traffic peaks at any time are probably contributed by small numbers of adjacent compute nodes.

Spatially bursty I/O could have been harmless to system I/O efficiency. However, the newly adopted I/O forwarding architecture introduces some novel I/O characteristics

<sup>1045-9219 2020</sup> IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

![](_page_1_Figure_1.png)

Fig. 1. I/O forwarding architecture on HPC systems. Each I/O node serves a fixed subset of adjacent compute nodes.

and may not effectively handle spatial I/O bursts. I/O forwarding infrastructure is an I/O layer sitting between compute nodes and the underlying storage system, as illustrated in Fig. 1. A subset of compute nodes, which are often located in the same rack, first send their I/O requests to the only I/O node assigned to them, then the I/O node forwards the requests to the storage system. I/O forwarding layer significantly reduces the number of I/O clients and dramatically promotes the performance and stability of the storage system [17]. It further provides opportunities for aggregating, caching or rescheduling I/O requests on I/O nodes [18]. Owing to the above advantages, I/O forwarding architecture has been adopted by 9 of the top 20 supercomputers in the TOP500 list of June 2019 [19].

Spatially bursty I/O poses two problems due to the I/O forwarding architecture. First, adjacent compute nodes often share the same I/O node, so when spatial I/O bursts arrive, a small number of I/O nodes serving the compute nodes with massive I/O can be heavily loaded. These I/O nodes can easily become bottlenecks while other I/O nodes have little workload to handle. Second, spatially bursty I/O leads to only a small number of I/O nodes intensely interacting with the storage system. As a result, the parallel performance of I/O forwarding layer cannot be fully exploited even if it is not overloaded.

To address the problems brought by spatially bursty I/O, we propose two approaches suitable for different platforms. The first one is remapping the I/O nodes. We statically map adjacent compute nodes to different I/O nodes so that the spatial I/O bursts can be directed to more I/O nodes. The second approach is to reallocate the compute nodes for jobs, which has no hardware requirements. We extract the I/O characteristics of applications from history I/O traces, and then use them to distribute the compute nodes more sparsely for jobs with certain characteristics. By mobilizing more I/O nodes to participate in the I/O activity, both approaches can balance the load on I/O nodes while making full use of their parallel I/O capability.

The rest of the paper is organized as follows. In Section 2, we introduce the platforms and I/O traces. We look into the causes of spatially bursty I/O in Section 3 and then present its evidence and discuss its impacts in Section 4. The two proposed solutions are provided in Sections 5 and 6. Section 7 contains a detailed evaluation. Related work is discussed in Section 8.

| Category | Trace Fields |
| --- | --- |
| CPU | load average |
| Memory | total, used, free |
|  | shared, buffers, cached |
| Lustre | read/write bytes |
|  | read/write counts |
|  | osc read/write bytes |
|  | osc read/write counts |
| Network | recieve/transmit bytes, |
|  | recieve/transmit packets |

# 2 PLATFORMS AND TRACES

# 2.1 Platform Overview

Tianhe-1A. Tianhe-1A in National Supercomputer Centre in Tianjin (NSCC-TJ) is the top 1 system in the TOP500 list of November 2010. It serves users in a variety of fields of both academia and industry. On Tianhe-1A, there are 64 compute nodes in each cabinet. Each compute node has 2 Intel Xeon X5670 CPU and 12 cores. Compute nodes and the Lustre storage system are connected through the highspeed interconnect network [20], with a hierarchical fat-tree topology [21]. It is noteworthy that Tianhe-1A has no I/O forwarding layer. However, I/O forwarding layer is completely transparent to jobs. With or without it, jobs are scheduled and mapped in the same way and leave the same I/O traces on compute nodes. Therefore, we can treat Tianhe-1A as a system with I/O forwarding layer by assuming that 64 compute nodes in the same cabinet are connected to a hypothetical I/O node when analyzing the I/O characteristics of I/O nodes.

CS19. CS19 is a supercomputer located in the China Aerodynamics Research and Development Center (CARDC) and is specifically used by computational fluid dynamics (CFD) applications. It has 11,392 compute nodes, each two of which share an FT-2000 CPU and 32 cores. There are 89 I/O forwarding nodes implemented with Lustre LNET routers. LNET routers are called I/O nodes for the remainder of the paper. Each I/O node serves 128 compute nodes in 2 compute frames. To be consistent with the description of Tianhe-1A, we regard the 128 compute nodes as located in a same cabinet and each cabinet connects to an I/O node. Compute nodes, I/O forwarding nodes and the Lustre storage system are connected via a 2-dimensional fat-tree topology.

#### 2.2 I/O Traces

We deployed an enterprise-class open-source monitor system Zabbix on Tianhe-1A and CS19 to collect I/O traces. The /proc file system on the compute node records all sorts of system kernel information, including Lustre I/O traffic, network traffic, CPU and memory usage, etc. Zabbix daemon processes on the compute nodes obtain such status data from /proc and then send it to Zabbix server at an interval of 10 seconds. The detailed traces we collected are listed in Table 1. We collect I/O traces of 5,677 compute nodes on Tianhe-1A for a period of 24 days (from December

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

distribution as follows.

TABLE 2 Job Logs Collected From Slurm

| Category | Log Fields |
| --- | --- |
| ID | JobID, JobName, UID, User |
| Time | Submit, Eligible, Start, End |
| Resource | ReqCPUS, AllocCPUS, NodeList |
| State | State |

11, 2017 to January 5, 2018). On CS19, we collect its I/O traces of 11,392 compute nodes for a period of 29 days (from February 27, 2019 to March 27, 2019) in the default mapping. After we implement the proposed remapping mechanism on CS19, we collect its I/O traces for a period of 21 days (from June 19, 2019 to July 10, 2019).

### 2.3 Job Logs

Both Tianhe-1A and CS19 use a job scheduling system called Slurm [22] to deliver computing power to applications. Slurm records the information of all jobs processed by the system, including job ID, job name, user name, the number and names of allocated nodes, the start and end time, etc. We collect the Slurm job logs of Tianhe-1A over 3 years (from January 2015 to January 2018) and job logs of CS19 over 3 years (from July 2016 to July 2019). The detailed logs are listed in Table 2.

# 2.4 Job Behaviors

Compute nodes are exclusively allocated to jobs on Tianhe-1A and CS19, which means that only one job can run on a compute node at the same time. Therefore, we can obtain a job's behaviors in the granularity of compute nodes by combining its start time, end time and allocated nodes with the I/O traces on those compute nodes. The job behaviors are later used to identify its I/O and network characteristics. We analyze the whole time periods of traces and logs if not otherwise specified.

# 3 CAUSES OF SPATIALLY BURSTY I/O

### 3.1 Measuring Unevenness of Distributions

As mentioned above, spatially bursty I/O is mainly caused by varying I/O demands of job's different processes and Slurm's strategy of allocating adjacent compute nodes. Therefore, to quantitatively analyze the causes, we need a mathematical model to measure the unevenness of job I/O traffic distribution and job node distribution.

Information entropy [23] is defined as the average amount of information of a random variable, and also refers to the disorder or uncertainty of a probability distribution. Shannon defined the entropy H of a discrete random variable X with possible values fx1; ... ; xng and probability mass function PðXÞ as

$$H(X)=-\sum_{i=1}^{n}P(x_{i})\log P(x_{i}).\tag{1}$$

The more uncertain a random variable, the more uniform its distribution so the larger its information entropy. Uniform distribution with n possible values has the largest entropy of log n based on Equation (1). Therefore, information entropy is a well-grounded measure for the evenness of a distribution. We can define the unevenness degree of a

Definition 1 (Unevenness Degree). X and U are two discrete probability distributions with n possible values. U is a uniform distribution. The unevenness degree of X is

$$UD(X)=H(U)-H(X)=\log n-H(X).\tag{2}$$

A UD of 0 indicates that distribution X is identical to the uniform distribution and thus it is very even. The larger the UD the more uneven X is.

Kullback-Leibler divergence [24], which is also known as relative entropy, is a measure of the difference between two probability distributions. A divergence of 0 indicates that the two distributions in question are identical. The larger the divergence is, the more different the two distributions are. Actually UD is mathematically equivalent to the Kullback-Leibler divergence from X to U. Therefore our definition of UD is mathematically sound.

The I/O traffic distribution or node distribution of different jobs may have different numbers of possible values since their numbers of processes and nodes can be different. As a result, their UDs have different value ranges, which makes them difficult to compare. We define normalized unevenness degree as follows to make UD in the range of [0,1].

Definition 2 (Normalized Unevenness Degree). X and U are two discrete probability distributions with n possible values. U is a uniform distribution. The normalized unevenness degree of X is

$$\text{NUD}(X)=\frac{\text{UD}(X)}{H(U)}=1-\frac{H(X)}{\log n}.\tag{3}$$

NUD is only monotonic for distributions with the same number of possible values based on the above definition. The NUDs of two distributions with different numbers of possible values are not comparable since they have different log n values. Its accurate definition is beyond the scope of this paper and here we only use NUD to compare distributions with the same number of possible values.

#### 3.2 Uneven Distribution of Job I/O Traffic

Large-scale HPC applications use thousands of parallel processes to split scientific computation. The I/O demands of different processes can be different although their computation is likely to be similar. We can obtain a job's I/O traffic distribution on its compute nodes by retrieving the Lustre I/O traffic data from the job's allocated nodes during its running. In this way, the I/O traffic distributions of all jobs can be obtained and further analyzed.

# 3.2.1 Rank 0 I/O

Rank 0 I/O [7] is a pattern that only the job's root process reads or writes data. It is common in the following two kinds of scientific applications. First, applications utilizing non-parallel high-level I/O libraries (e.g., serial HDF5 and NetCDF) have to read input data and write output data Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

![](_page_3_Figure_1.png)

Fig. 2. The I/O traffic distribution NUDs of all jobs with all rank I/O pattern.

with the root process. Second, applications that need to reduce the data located in all the processes also exhibit rank 0 I/O pattern, because the reduction (e.g., summing or sorting) must eventually be completed on one process and the results will be written out by that process. Rank 0 I/O will lead to I/O traffic concentrating on only one compute node even if a job runs on multiple ones.

For each compute node allocated to a job, we calculate its proportion of I/O traffic amount to the job's total amount. If the largest of all the proportions of compute nodes exceeds 95 percent, the job is considered to exhibit rank 0 I/O pattern. We investigate all multi-node jobs and find that there are 25.7 percent of jobs on Tianhe-1A and 6.6 percent of jobs on CS19 only use one of its multiple compute nodes to perform most of the I/O. These jobs can only utilize one I/O node to forward their I/O traffic even if their compute nodes are mapped to multiple ones. It causes spatially bursty I/O and will result in critical load imbalance and the potential of I/O bottlenecks.

# 3.2.2 All Rank I/O

As opposed to rank 0 I/O, all rank I/O is a pattern that all the job's processes participate in I/O. Although 74.3 percent of jobs on Tianhe-1A and 93.4 percent of jobs on CS19 exhibit all rank I/O pattern, their I/O traffic can still be distributed on compute nodes unevenly. We investigate the unevenness of the I/O distributions of jobs with all rank I/O pattern by calculating their NUDs. Their NUD values are shown in Fig. 2 from large to small. However, a larger NUD value does not necessarily mean a more uneven I/O traffic distribution. As mentioned in Section 3.1, the definition of NUD determines that it is not comparable between jobs that have different numbers of compute nodes.

To find out the proportion of jobs that have uneven I/O traffic distribution, we group the jobs by their numbers of nodes and determine a NUD threshold for each group. Any job with a NUD larger than the threshold of its group is considered to have uneven I/O traffic since NUD is monotonic for distributions with the same number of possible values. Thereby, we thoroughly examine the I/O traffic distributions in every group and try to find the proper thresholds. We demonstrate the I/O traffic distributions of 4 jobs which have NUDs around 0.05 in Fig. 3. Although they run on different numbers of nodes, their traffic distributions are all very uneven. In fact, we find that 0.05 is a suitable NUD threshold for all groups after an examination. Therefore, we set a universal NUD threshold of 0.05 for all jobs. Any job that has a larger NUD will have more uneven I/O traffic distribution. The results in Fig. 2 indicate that about 61.9 and 52.9 percent of jobs on Tianhe-1A and CS19 have even I/O traffic distributions. The I/O traffic of the rest 38.1 and 47.1 percent of jobs is concentrated on a subset of their compute nodes, and thus they will probably cause load imbalance on the I/O nodes which their compute nodes are mapped to.

#### 3.3 Uneven Distribution of Job Nodes

Job scheduling systems select and allocate the most appropriate compute nodes to submitted jobs based on their specific requirements (e.g., number and types of compute nodes, memory capacity, etc.). It is possible that the compute nodes allocated to a job are unevenly distributed on multiple cabinets. Since the compute nodes on the same cabinet share the same I/O node on HPC systems, the job's I/O traffic will be unevenly directed to multiple I/O nodes, which causes spatially bursty I/O. We retrieve the node list data from the job logs in Slurm database and investigate the node distributions of all jobs on Tianhe-1A and CS19 over 3 years.

# 3.3.1 Concentrated Distribution

Slurm allocates compute nodes to jobs with a best-fit algorithm based on the number of consecutive nodes. Moreover, Slurm offers plugins for multiple network topologies [25], including torus, fat-tree, etc. For example, in the fat-tree network of Tianhe-1A and CS19, the Slurm plugin attempts to locate a job's compute nodes in the least number of leaf switches. The best-fit strategy and the plugins of Slurm strive to minimize the communication overheads by allocating jobs with large chunks of compute nodes locating close to each other. Therefore, for a job that runs on N nodes, Slurm tends to place its nodes on a minimal number of dN=64e cabinets. In production systems, lots of jobs compete for a limited number of nodes, so it is possible that a job is

![](_page_3_Figure_13.png)

Fig. 3. I/O traffic distributions of four jobs with NUD around 0.05.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

![](_page_4_Figure_1.png)

Fig. 4. The proportions of different-sized jobs locating in minimal number of cabinets.

located in more cabinets than its minimal number. We obtain the number of cabinets a job's nodes are actually located in and calculate its minimal number. The proportions of different-sized multi-node jobs whose nodes are located in a minimal number of cabinets are shown in Fig. 4. The jobs that have 2n1 þ 1 to 2n nodes are classified to the n group in the figure.

2As can be seen from Fig. 4, smaller jobs are more likely to be located in a minimal number of cabinets. As the job size grows, it is increasingly impossible to fit its nodes in the minimal number of cabinets. There is an abnormal situation on Tianhe-1A at the size of 128 nodes. Jobs of such size are more likely to fit because its cabinet number increases from 1 to 2 for the first time as the node number grows. The statistics show that the compute nodes of about 70.4 percent of multi-node jobs on Tianhe-1A and 49.2 percent of multi-node jobs on CS19 are only located in minimal numbers of cabinets. These jobs' I/O traffic are concentrated on a small number of I/O nodes, resulting in spatially bursty I/O.

# 3.3.2 Uneven Distribution

For the jobs whose compute nodes are located in multiple cabinets, the node distribution on cabinets can be uneven. We calculate the NUDs of all multi-cabinet jobs, as presented in Fig. 5. Similar to Section 3.2.2, we choose a universal NUD threshold of 0.05 for all jobs with different numbers of cabinets after a thorough examination. We select 4 example jobs whose NUD is around 0.05 and display their node distributions in Fig. 6. In the figures we can find that these jobs' node distributions are all very uneven. Any job with a larger NUD will have more uneven node distribution. The results in Fig. 5 show that about 50.7 percent of multi-cabinet jobs on Tianhe-1A and 71.3 percent of multi-cabinet jobs on CS19 have uneven node distributions. These jobs' I/O traffic distributions on their

![](_page_4_Figure_7.png)

Fig. 5. The node distribution NUDs of all multi-cabinet jobs.

cabinets will probably be uneven, too. It will cause spatially bursty I/O and make the I/O nodes load imbalanced.

# 4 SPATIALLY BURSTY I/O AND ITS IMPACTS

# 4.1 Evidence of Spatially Bursty I/O

The uneven distribution of job I/O traffic makes the I/O traffic concentrated on one or a minority of compute nodes, and the uneven distribution of job nodes make the compute nodes concentrated on one or a minority of cabinets. Both causes have made the I/O traffic of the whole system concentrated on a small number of adjacent compute nodes, resulting in spatially bursty I/O. Based on the collected I/O traces, we have observed evident spatially bursty I/O on both Tianhe-1A and CS19.

Fig. 7a shows the total I/O traffic handled by the compute nodes in each cabinet on Tianhe-1A. There are I/O nodes on CS19, so we collect the I/O traces on real I/O nodes and demonstrate their I/O distribution in Fig. 7b. It can be seen that different cabinets or I/O nodes have very different I/O workloads. Even adjacent cabinets or I/O nodes differ in the amount of processed I/O traffic, which results in critical load imbalance.

Different amounts of total I/O traffic do not indicate that the cabinets or I/O nodes have uneven I/O traffic all the time. At every time interval, we find out the top 1 percent compute nodes that issued the most I/O traffic at that time interval, and calculate the percentage of their I/O amount to the system's total amount. The results show that the top 1 percent nodes contribute 90.8 percent of the traffic on Tianhe-1A and 96.6 percent of the traffic on CS19. The I/O traffic of the system is concentrated dramatically in the space dimension.

However, it still won't cause load imbalance on I/O nodes if these top 1 percent compute nodes are evenly distributed in

![](_page_4_Figure_16.png)

Fig. 6. Node distributions of four jobs with NUD around 0.05. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

![](_page_5_Figure_1.png)

the system. We further calculate the I/O traffic proportion of the top 20 percent cabinets, which is shown in Fig. 8. The top 20 percent most I/O-intensive cabinets contribute about 80 percent of the total I/O traffic at all time intervals on both Tianhe-1A and CS19, which means that the top 1 percent compute nodes are unevenly distributed in the system. It can be concluded that the I/O traffic handled by the cabinets or I/O nodes are uneven all the time. Spatially bursty I/O constantly exists on both Tianhe-1A and CS19.

#### 4.2 Impacts of Spatially Bursty I/O

The I/O forwarding infrastructures designed by different supercomputer vendors usually have different architectures and implementations. Despite that, their mappings of compute node to I/O node are all about the same. A subset of compute nodes locating close to each other in the network are mapped to a single I/O node [26], [27], [28], [29], as illustrated in Fig. 1. This simple mapping is easy to understand, manipulate and manage. It even enables some systems, such as BlueGene [26], to set up a dedicated I/O network connecting compute nodes and their assigned I/O node. However, under this mapping, the spatially bursty I/O characteristic of the system would cause the following two kinds of critical performance impacts to I/O forwarding layer.

#### 4.2.1 Load Imbalance

Temporally bursty I/O has made the storage system suffer from handling I/O traffic beyond its capability. When the I/O burst arrives, there is not enough time for the storage system to ingest such a tremendous amount of I/O traffic immediately. What's worse, the spatially bursty I/O aggravates such incompetence. Since the I/O bursts come only from some adjacent compute nodes and these nodes probably share a same I/O node, there are only a small number of I/O nodes processing the I/O bursts. As the observation on Tianhe-1A and CS19 in Fig. 8 represents, 20 percent I/O nodes handle 80 percent I/O traffic of the system at any given moment. It means that about 80 percent procurement of I/O nodes is wasted since they have little workload to process. Even worse, we cannot cut this part of procurement since all the I/O nodes take turns as the busiest ones. Theses busy I/O nodes can easily become I/O bottlenecks and impede the running of applications.

#### 4.2.2 Underutilization

Most supercomputers adopt a parallel file system, such as Lustre, GPFS and PVFS, as their underlying storage [30]. Take Lustre, the most widely adopted file system in supercomputers, as an example. On Lustre, files are striped across many object

![](_page_5_Figure_10.png)

Fig. 7. I/O distribution on all cabinets. Fig. 8. I/O percentage of top 20 percent cabinets.

storage servers (OSS), which concurrently serve data requests from clients. Although a single client can take advantage of the file striping and access data from multiple OSSs in parallel, due to the limited network bandwidth and other latencies in the I/O path, the best I/O performance can only be achieved by multiple clients accessing data from multiple OSSs [31], [32]. After inserting the I/O forwarding layer, the I/O nodes act as the clients of Lustre in place of compute nodes. Similarly, applications can achieve better I/O performance if more I/O nodes are utilized to access data from Lustre. Prior work has also observed such similar underutilization on a Cray system [33].

Due to spatially bursty I/O, there are only about 20 percent I/O nodes busy accessing data from Lustre. The rest 80 percent are seriously under utilized. It can be concluded that the performance of the I/O subsystem is not used to the full, leaving much scope for further improvements.

# 5 REMAPPING I/O NODES

### 5.1 Approach Overview

Since the mapping of compute nodes to I/O nodes is the reason leading to spatially bursty traffic concentrated on a smaller number of I/O nodes, remapping the I/O nodes is a straightforward approach to address this issue.

In the original mapping, the compute nodes in the same cabinet are mapped to a same I/O node. As illustrated in Fig. 9, compute node i is mapped to I/O node bi=ðm=nÞc, where m is the total number of compute nodes and n is the total number of I/O nodes. We propose to map adjacent compute nodes to different I/O nodes. Compute node i is instead mapped to I/O node i%n. For each I/O node, the number of its serving compute nodes remains the same after remapping, but they are now distributed sparsely throughout the system rather than located closely in a minority of cabinets. When spatial I/O bursts arrive, the traffic generated from adjacent compute nodes will be redirected to many more I/O nodes. Therefore, it achieves better load balance and higher parallel I/O performance.

![](_page_5_Figure_18.png)

Fig. 9. The mappings of compute nodes to I/O nodes. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

### 5.2 Influences on Network

Despite that most supercomputers have the same compute to I/O node mapping, their interconnect network and placement of I/O nodes differ. Therefore our remapping mechanism may have different influences on them. In this section, we discuss the network influences on CS19 and other two major series of supercomputers, BlueGene and Cray. Since our approach do not involve the network between I/O nodes and storage nodes we only need to analyze the distance between compute nodes and I/O nodes.

On CS19, 64 compute nodes on a frame are connected to one switch board, named NRM (Network Router Module), and NRM boards are interconnected with a 2-dimensional fat-tree network. The route between NRM boards on the same column or the same row requires just 2 hops. The route between NRM boards on different columns and rows requires 4 hops. I/O nodes are placed in 6 NRM boards in a row. We calculate the actual average route hops between compute nodes and their corresponding I/O nodes on CS19. It is 3.655 in the original mapping and 3.634 after remapping. Therefore the remapping will not increase the network distance of I/O requests. On the contrary, the remapping will balance the traffic load on the NRM boards of I/O nodes and promote their stability since the spatially bursty traffic is directed to more I/O nodes more evenly.

On BlueGene systems, e.g., BlueGene/Q Mira, compute nodes are split into psets. A pset consists of 128 compute nodes, which are connected to a same I/O node through a dedicated I/O network [34]. This design separates the I/O traffic from communication traffic and minimizes the network overheads between compute nodes and I/O nodes. Our remapping approach cannot be applied to BlueGene/Q systems since their compute nodes are hard-wired to only one I/O node and cannot be remapped to another one.

On Cray systems, e.g., Cray XC40 Cori, compute nodes are split into groups interconnected with a dragonfly network. Its I/O nodes, i.e., compute nodes acting as Lustre LNET routers, are placed in several groups [27]. The dragonfly topology is centrosymmetric, where the numbers of route hops between any two compute node groups are the same.

Moreover, even if the network distance between compute nodes and I/O nodes changes a lot, in the I/O path the network overheads is negligible compared to the I/O overheads of accessing data from spinning disks. Therefore, the remapping will not change the average network distance in the I/O path or increase the I/O overheads.

# 6 REALLOCATING COMPUTE NODES

Although it is easy to implement and manage, the mechanism of remapping I/O nodes is platform-dependent. It cannot be deployed on HPC systems, e.g., BlueGene systems, where the I/O node mapping is difficult to change. Therefore, we propose the mechanism of reallocating compute nodes which has no hardware requirements.

#### 6.1 Approach Overview

In the two causes of spatially bursty I/O, the uneven distribution of job I/O traffic is determined by the inherent nature of the job and is difficult for system administrators to modify. We thus try to address the problem of uneven node distribution by reallocating the compute nodes for submitted jobs.

TABLE 3 The Proportions of Jobs That Have three Characteristics and Jobs That Can be Optimized by Reallocation Mechanism

| Platform | Data-intensive | All rank I/O | Low-Comm | Optimizable |
| --- | --- | --- | --- | --- |
| Tianhe-1A | 7.2% | 42.7% | 93.3% | 6.3% |
| CS19 | 30.1% | 44.4% | 95.3% | 24.0% |

As mentioned in Section 3.3.1, the node allocation strategy of the job scheduling system assigns adjacent nodes for jobs by default to minimize communication overheads. It makes jobs utilize fewer I/O nodes and causes load imbalance and poor parallel I/O performance. We propose to scatter the job's compute nodes to utilize more I/O nodes. Furthermore, we regroup the compute nodes by their I/O traffic so that I/O nodes can be more load balanced.

In this paper, we refer to the programs submitted by users as jobs. For any two jobs, if they have the same submitter, job name and job size, they are considered to belong to the same application. The basic idea of our approach is to identify the I/O characteristics of applications by collecting and analyzing the I/O traces of their history jobs. When a new job is submitted, if its application is considered to benefit from our approach, we place its compute nodes on more I/O nodes with more balanced traffic loads.

#### 6.2 Characteristics of Optimizable Jobs

Not all jobs can benefit from our compute node reallocation scheme. To be specific, only jobs with the following I/O characteristics are optimizable.

Data-Intensive Jobs. This prerequisite is obvious since only data-intensive jobs are impeded by load imbalance and underutilization of I/O nodes. A job is considered to be dataintensive if its total amount of I/O traffic exceeds a threshold.

All Rank I/O Jobs. If a job has rank 0 I/O pattern, its I/O traffic is handled by only one compute node. All the traffic will be directed to only one I/O node no matter how we reallocate its compute nodes. Therefore, only jobs with all rank I/O pattern can benefit from our approach.

Low-Communication Jobs. Scattering the compute nodes more sparsely will inevitably increase the communication overheads of jobs [35]. If the increased overheads exceed the I/O benefits, this job will not benefit from our approach. A job is considered to be low-communication if its amount of I/O traffic exceeds its communication traffic.

We investigate all the jobs on both Tianhe-1A and CS19 to calculate the proportion of optimizable jobs. Table 3 represents the proportions of the jobs that have 3 characteristics in all jobs. The results indicate that only 7.2 and 30.1 percent of jobs are data-intensive. However, they contribute 98.1 and 91.0 percent of the total I/O traffic on Tianhe-1A and CS19 respectively. It can significantly promote the system I/O efficiency even if we can only reallocate the compute nodes of the limited number of data-intensive jobs. The proportions of the optimizable jobs that satisfy all the 3 characteristic requirements are 6.3 and 24.0 percent.

# 6.3 Consistencies of Application Characteristics

Even if the jobs are grouped into applications by their users, job names and job sizes, the jobs of the same application may Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

![](_page_7_Figure_1.png)

Fig. 10. I/O characteristic consistency degrees of all multi-node applications that have more than five jobs.

still have different I/O characteristics, since users often run the same application multiple times with varying input data and parameters to get the best results [36]. The prerequisite of our approach is that the new jobs will have the same characteristics as the history jobs of the same application. Therefore, we must inspect the consistency of application characteristics.

We define the I/O characteristic consistency degree of an application as follows.

# Definition 3 (I/O Characteristic Consistency Degree).

Among all the jobs of an application, if the percentage of jobs with a certain I/O characteristic is p, and the percentage of jobs without the characteristic is 1 p, then the I/O characteristic consistency degree of this application is maxfp; 1 pg.

If an application's consistency degree is very low, e.g., 50 percent, two halves of its jobs have different I/O characteristics. The application's characteristic is very inconsistent and the characteristic of a new job is unpredictable. If the consistency degree is 100 percent, then all its jobs have the same characteristic. It is reliable to presume that a new job of this application will also have this characteristic.

We calculate the consistency degrees of data-intensive, all rank I/O and low-communication characteristics of all multi-node applications that have more than 5 jobs. The results in Fig. 10 show that the vast majority of applications have very high consistency degrees. It proves that the applications' characteristics can be used to predict their new jobs. Although there is a small chance that a new job of an optimizable application does not have the required characteristics, it will not suffer serious performance impact when its nodes get reallocated by our reallocation strategy. Specifically, if a job is not data-intensive or does not present all rank I/O characteristic, it will neither be optimized nor harmed by our reallocation strategy. If a job has a lot of communication, its performance impact is also limited as will be evaluated later in Section 7.2.2.

As we try to reallocate the compute nodes according to their I/O traffic distribution so that the load on I/O nodes can be more balanced, the traffic distributions of applications should also be consistent. We define the I/O distribution divergence as follows.

#### Definition 4 (I/O Traffic Distribution Divergence). For

an application that runs on N compute nodes, the I/O traffic distributions on the compute nodes of its M jobs can be regarded as M vectors in the N-dimensional space. The euclidean distance between any two vectors measures their divergence. The average of the C2 M distances between each two of the M vectors is the I/O traffic distribution divergence of this application.

![](_page_7_Figure_12.png)

Fig. 11. I/O traffic distribution divergences of all multi-node applications that have more than five jobs.

We calculate the I/O traffic distribution divergences of all multi-node applications that have more than 5 jobs, as shown in Fig. 11. We manually select 0.3 as the threshold to determine whether the I/O traffic distribution is consistent after carefully examining the distributions of all applications. In Fig. 12 we plot the heat map of 2 applications that run on 2 compute nodes. As can be seen from the figure, the traffic distribution tends to be different when the divergence grows larger than 0.3.

# 6.4 Node Allocation Strategy

#### 6.4.1 Even Node Strategy

Fig. 11 shows that the I/O traffic distributions of 29.4 percent of applications on Tianhe-1A and 23.6 percent applications on CS19 are divergent and cannot be used to predict their new jobs. Still, new jobs of these applications have the opportunity to be optimized by our baseline even node strategy, if they are in the category of optimizable jobs described in Section 6.2. Under the even node strategy, we split job nodes into groups of the same number of nodes and assign them to respective I/O nodes, so that the originally concentrated I/O traffic will be directed to more I/O nodes more evenly.

# 6.4.2 Even Traffic Strategy

For the rest applications with consistent I/O traffic distributions, the I/O traffic distributions of their new jobs are predictable. Their new jobs have the opportunity to be optimized by our even traffic strategy, a more fine-grained node allocation strategy. If they are in the category of optimizable jobs described in Section 6.2, we split their new jobs' nodes into groups with about the same amount of I/O traffic and assign them to respective I/O nodes, so that the load on I/O nodes can be further more balanced.

![](_page_7_Figure_20.png)

Fig. 12. I/O traffic distributions of two two-node applications with divergence around 0.3.

| TABLE 4 |
| --- |
| Numbers of Compute Nodes and I/O Nodes in Different Settings |

| Settings | # Compute Nodes | # I/O Nodes | # ION for m CN |
| --- | --- | --- | --- |
| Original | 64 | 1 | 1 |
| Remap | 64 | 64 | m |
| Reallocate | 64 | 64 | m |

### 6.4.3 Span of Job Node Distribution

The diversity of idle compute nodes, i.e., the number of different I/O nodes connected to them, is a scares resource. Because on busy production systems, such as Tianhe-1A and CS19, there are only a few idle compute nodes left at any time. Therefore we should assign adequate number of I/O nodes to the current job while reserving diversity for upcoming jobs.

Our reallocation strategy follows the steps below to decide the number of I/O nodes. (1) It tries to provide more I/O nodes for the current job than the Slurm's default strategy, or the node allocation strategy rolls back to the default strategy of Slurm. (2) It tries to reserve 1/3 to 2/3 of I/O node diversity for upcoming jobs. If the next optimizable job in the queue is larger than twice the size of the current job, it reserves 2/3 of the diversity. If it is smaller than half the size of the current job, it reserves 1/3 of the diversity. If the diversity is not enough to be reserved, it preferentially satisfies the need of the current job. (3) It tries not to assign too many I/O nodes for the current job. If the average number of the job's compute nodes served by an I/O node is less than 8, it shrinks the number of I/O nodes. The threshold is set to 8 because we find that generally 4 to 8 I/Ointensive compute nodes will overload an I/O node.

# 7 EVALUATION

# 7.1 Testbed

The performance evaluations are all conducted on CS19 in CARDC. We have implemented the proposed I/O node remapping mechanism on it for 11 months. The numbers of compute nodes and I/O nodes we used in different test settings are shown in Table 4. All the evaluations are conducted under this configuration except for the test of the influence of I/O distribution in Section 7.2.3, which will be discussed in detail in that section.

![](_page_8_Figure_9.png)

In the proposed mapping, since CS19 has 89 I/O nodes, every 89 adjacent compute nodes are mapped to the I/O nodes in a round-robin manner. We use 64 compute nodes, each of which is mapped to a different I/O node.

For the reallocation strategy, we implement a prototype Slurm plugin that adopts the proposed node allocation strategy and run it on a private Slurm server. The private server manages 512 compute nodes and only handle our job submissions in the experiments. These compute nodes are grouped into 64 groups, which are mapped to 64 different I/O nodes. The actual maximum number of compute nodes used is 64 (1 compute node in each group) in all the tests due to our maximum test scale. We reserve 512 idle compute nodes to test whether our reallocation strategy can evenly distribute job nodes.

As shown in Table 4, for each experiment scale of m compute nodes in all the tests, there are m I/O nodes involved in the remapping and reallocation settings and only 1 I/O node in the original setting, except for the evaluation in Section 7.2.3.

# 7.2 Microbenchmark

In this section we use IOR [37] and synthetic benchmarks to evaluate the performance. There are 8 benchmark processes running on each compute node. The I/O size is 1 MB. We use direct I/O to eliminate the influence of memory cache.

# 7.2.1 Baseline Performance

We first benchmark the baseline performance with IOR, a widely used I/O benchmark in large scale systems. As shown in Fig. 13a, both the remapping and reallocation mechanisms have significant performance promotion. In the original mapping, all the I/O requests are transferred through a single I/O node. The fierce I/O contention on this I/O node results in I/O bottleneck as the number of IOR processes grows. Both of our optimizations successfully mobilize multiple I/O nodes to share the I/O traffic. It verifies that better parallel I/O performance can be achieved by more Lustre clients (i.e., I/O nodes).

![](_page_8_Figure_17.png)

![](_page_8_Figure_20.png)

![](_page_9_Figure_1.png)

Fig. 14. Performance of Real Applications.

#### 7.2.2 Influence of Communication

The difference between the remapping and reallocation mechanisms is the communication distance between job processes. The I/O node remapping mechanism will not change the communication distance, while the node reallocation strategy will distribute the compute nodes more sparsely and hence increase the communication overheads.

In order to evaluate such influence of communication, we develop a synthetic benchmark. Each process accesses 1 GB of data and then communicates 8 GB of data with each other in an all-to-all manner with a transfer size of 32 bytes. The all-to-all communication is implemented with MPI_ Alltoall().

Fig. 13b shows the running time of the experiments. Solid bars represent the communication time, and hollow bars represent the I/O time. We have the following findings. (1) In both the original and proposed mapping, job nodes are located close to each other due to Slurm's default allocation strategy. As a result, their communication performances are better than the reallocation mechanism in the tests. (2) With our remapping and reallocation mechanisms, job nodes utilize more I/O nodes to access data, so that their I/O performances are better. (3) While our optimizations bring more and more remarkable performance advantage as the experiment scale grows, the remapping mechanism outperforms the reallocation mechanism since all its communication happens within a leaf router. (4) The I/O performance benefits brought by our node reallocation strategy exceed the increased network overheads. Therefore, only applications with communication demands far in excess of their I/O demands cannot benefit from our reallocation mechanism.

### 7.2.3 Influence of I/O Distribution

Our node reallocation mechanism includes two different strategies, even node strategy for applications with divergent I/O distribution, and even traffic strategy for applications with consistent I/O distribution. The even traffic strategy will further rearrange the compute nodes according to their I/O traffic so that the I/O nodes are more load balanced.

In order to evaluate such differences, we develop a synthetic benchmark. The I/O traffic of its processes is incremental. The relative I/O amounts of its n processes range from 1=n to 1. For each experiment scale of m compute nodes, the available number of I/O nodes is set to m=2, making 2 compute nodes share an I/O node. The even traffic strategy will try to allocate compute nodes with a Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

![](_page_9_Figure_10.png)

maximum number of I/O nodes while balancing the traffic of the I/O nodes. The even node strategy only simply distributes the compute nodes evenly on a maximum number of I/O nodes.

The running time of the benchmark is determined by the maximum of the individual compute process I/O times. Whether the busy process's I/O node is busy is crucial to the benchmark's overall performance. Under the even node strategy, the compute nodes are evenly distributed on the I/O nodes regardless of their different I/O burden. As a result, the busiest compute nodes are concentrated in the same I/O node, leading to intense I/O contention. The results in Fig. 13c show that the even traffic strategy outperforms the even node strategy by further balancing the loads on I/O nodes. It proves that although different compute nodes have independent I/O streams and their I/O nodes can process them concurrently, the I/O contention will impact their performance. It is better to balance the load on I/O nodes to alleviate I/O contention and achieve better parallel performance.

# 7.3 Real Application

In this section we use 2 real applications and 1 real applicationbased benchmark to evaluate our approaches. The I/O distributions of all the 3 applications are relatively even so that the performance of our even traffic strategy is about the same with the even node strategy. Therefore in the tests we only evaluate the even node strategy in the reallocation mechanism.

# 7.3.1 BTIO

BTIO [38] is an I/O kernel of a NASA's NAS parallel benchmark derived from CFD applications. It solves block-tridiagonal equations with a square number of processes. Each process is responsible for accessing multiple Cartesian subsets of the entire data set so that it generates a large amount of small I/O requests. In the tests, we use the collective I/O mode of BTIO and its default settings, which allows processes to send their small I/O requests to the collector in the same compute node. The collector will aggregate the requests and access data for them. There is 1 collector process on every compute node. The tests are weak scaling that problem size grows with the number of processes and the problem size per process is fixed.

Fig. 14a shows the test results. In the tests, we run 16 processes in each compute node. There is only 1 process performing I/O on each compute node due to the collective I/O

![](_page_10_Figure_2.png)

Fig. 15. Simulation with Tianhe-1A data.

optimization. When the experiment scale is small the I/O burden is relatively light, thus concentrated I/O traffic on a single I/O node will not affect the performance. As the experiment scale grows, the single I/O node becomes the bottleneck. The results show that both the remapping and reallocation mechanisms have better scale-out performances.

# 7.3.2 Weno3D

Weno3D [39] is a numerical simulation application that analyzes vortical flow by solving 3-dimensional unsteady Navier-Stokes equations. Each process needs to compute a sub matrix of a large 3-dimensional matrix and write the results every 100 steps. In every computation step, the process needs to communicate with 4 other processes which handle the neighboring sub matrixes. In the tests we run Weno3D on up to 64 compute nodes with 16 processes on each of them. The tests are weak scaling.

The results in Fig. 14b show that both the I/O node remapping and compute node reallocation mechanisms decrease the running time of Weno3D significantly. The promotion gets more remarkable as the test scale grows owing to that more I/O nodes are involved in forwarding the growing amount of data requests. The amount of communication is relatively small compared to the amount of I/O, so that the performance difference between the remapping and reallocation mechanisms is neglectable.

# 7.3.3 WRF

The Weather Research and Forecasting (WRF) model is a widely used numerical weather prediction system. A typical WRF run consists of 3 different phases, including reading input data and a parameter file, conducting simulations, and writing checkpoints and results. In this paper we test a WRF workflow that consists of thousands of simulation cycles. In each cycle, 2 different datasets are read and simulated by WRF and then some parts of the 2 written out result datasets are exchanged. The 2 exchanged datasets will be processed by WRF in the next cycle. The tests are strong scaling that the input data size is fixed to 27 GB with different numbers of processes.

Fig. 14c shows the test results. As a data-intensive application, the WRF workflow substantially benefits from both our remapping and reallocation mechanisms, especially with larger job sizes. As more I/O nodes participate in I/O Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

![](_page_10_Figure_12.png)

forwarding, the reading, writing and exchanging of datasets are accelerated more significantly. Meanwhile, the running time of computation-intensive simulation becomes the dominant part of total running time, so that the speedup is not so significant as the number of compute nodes grows.

#### 7.4 Load Balance

In this section, we evaluate the load balance effect of our proposed I/O node mapping mechanism with both simulations on Tianhe-1A and real experiments on CS19. As mentioned in Section 2.2, there are 24 days of I/O traces on Tianhe-1A. There are 29 days of traces before the optimization and 21 days of traces after the optimization on CS19. So we compare 21 days of traces on CS19.

#### 7.4.1 Simulation on Tianhe-1A

As we have collected the I/O traffic time series data of all compute nodes on Tianhe-1A, we can extract the I/O traffic distributions on hypothetical I/O nodes by assigning the I/O traffic of compute nodes to the I/O nodes they are mapped to. By using different assigning methods of different mapping mechanisms, we can compare their load balance of I/O nodes. As shown in Figs. 15a and 15b, our proposed I/O node mapping mechanism can significantly promote the load balance. It confirms that adjacent compute nodes often perform I/O concurrently and mapping them to different I/O nodes can effectively avoid spatially bursty I/O.

We further investigate whether compute nodes use I/O nodes more efficiently under our proposed mapping mechanism. Recall that the I/O traffic is also bursty in time. Only a small part of compute nodes are busy processing I/O at the same time. We investigate the 10 percent most dataintensive I/O nodes at any time interval and extract the proportion of their amount of I/O traffic to the total amount of I/O traffic of the system. The results in Fig. 15c reveal that the proposed mapping mechanism has decreased the proportion from 58.6 to 37.9 percent, which means that the I/O traffic is distributed much more evenly with our remapping mechanism.

### 7.4.2 Real Experiment on CS19

We implement the proposed I/O node mapping mechanism on CS19. It has been running stably for about 11 months. The I/O traces on I/O nodes before and after implementing

![](_page_11_Figure_1.png)

![](_page_11_Figure_4.png)

Fig. 16. Real experiment on CS19.

the mechanism are collected for evaluation. As shown in Figs. 16a and 16b, the load on I/O nodes is much more balanced under our proposed mapping. Since the even distribution of total I/O traffic may conceal the uneven real-time I/O traffic, we further investigate the real-time I/O traffic of the busiest 10 percent I/O nodes, and calculate the proportion of their amount of handled I/O traffic to the total amount. The results in Fig. 16c show that the proposed mapping mechanism reduces almost 1/3 traffic at all time intervals. It offloads the heavy I/O burden of busy I/O nodes to idle ones and reduces the gap between them, enabling more I/O nodes to participate in I/O forwarding.

# 7.5 I/O Interference

I/O interference often refers to the performance degradation observed by a single application when competing for shared I/O resources with other applications running on the same system [40]. There is a large body of work that detects and optimizes I/O interference on storage systems and I/O forwarding layer [29], [41], [42]. However, they mainly focus on I/O interference between applications. The more finegrained I/O interference between compute nodes is neglected.

In fact, a more accurate definition of I/O interference is the performance degradation caused by multiple clients competing for limited I/O resources. The clients can be compute nodes of different applications or even the same application. Moreover, I/O interference between nodes of different applications is often not as fierce as nodes of the same application, since their I/O phase may not overlap or they may have orthogonal resource usage patterns [29]. Compute nodes of the same application often synchronously access the same I/O resource at the same time, so their I/O interference is much more dramatic.

Our proposed I/O node mapping and compute node allocation mechanisms make applications utilize more I/O nodes. It inevitably increases the probability that different applications use the same I/O nodes. However, it does not necessarily aggravate the I/O interference. The probability that different compute nodes compete for the same I/O node does not necessarily increase.

In order to quantify the impact on I/O interference of our proposed approach, we analyze the situations of compute nodes sharing I/O nodes. We select the busiest 1 percent compute nodes on CS19 at every time interval and count the number of different I/O nodes they are mapped to. Recall that the busiest 1 percent compute nodes contribute 96.6 percent I/O traffic. Therefore they represent almost all the I/O activities of the entire system. Fig. 17a shows that at every time interval the number of used I/O nodes in the proposed mapping is about twice as many as the original mapping. With more active I/O nodes, the average number of compute nodes served by an I/O node is greatly reduced. So the I/O interference on the I/O nodes is mitigated.

We further show what fraction of I/O nodes are in use with heat maps in Figs. 17b and 17c. If an I/O node at a time interval serves more compute nodes which are part of the busiest 1 percent nodes, it is represented with hotter color. As shown in the figures, the busiest 1 percent compute nodes are concentrated on only a small portion of I/O nodes in the original mapping. The I/O contentions on

![](_page_11_Figure_15.png)

Fig. 17. Evaluations of I/O interference on CS19. We select the busiest 1 percent compute nodes at every time interval and count the number of their used I/O nodes and the number of busy compute nodes served by each I/O node. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply. these I/O nodes are fierce since there are a lot of active compute nodes competing their I/O resources. By mapping adjacent compute nodes to different I/O nodes our proposed mapping successfully directs the spatial I/O bursts to many more I/O nodes. The busy compute nodes are distributed more evenly on the I/O nodes, resulting in alleviated I/O interference.

Above evaluations indicate that the new mapping will mitigate rather than aggravate the I/O interference on the I/O nodes.

# 8 RELATED WORK

Ever since I/O forwarding technique is introduced, a wide range of systems, e.g., Cray XC, BlueGene and Tianhe-2, etc., have adopted I/O forwarding layer in their I/O software stack, which stimulates a lot of research interests both in industry and academia. Burst Buffer [13] stages data in the flash devices attached to I/O nodes. Ohta et al. [43] try to accelerate the transferring on I/O nodes with request pipelining and merging. Vishwanath et al. [44] propose a workqueue model and an asynchronous data staging strategy to enhance the I/O forwarding on a BlueGenegP system.

There is some research on balancing the load on I/O nodes. Yu et al. [45], [46] propose a cross-layer I/O coordination strategy, which enables a job's compute nodes to access different data stripes from different I/O nodes simultaneously. Its drawback is that it can only balance the load on the I/O nodes used by a job. When a job only uses a minority of I/O nodes, the parallel performance is still limited. Jiet al. [29] propose an automatic mechanism for application-adaptive dynamic forwarding resource allocation. It grants data-intensive jobs more I/O nodes or dedicated I/O nodes by changing the I/O node mapping dynamically before jobs are about to run. Our first approach of remapping I/O nodes has a similar idea except that we set the mapping statically. Without complex workload-aware mechanism and online configuring I/O nodes, our approach achieves similar promotion of performance and mitigation of interference. In addition, both the above 2 approaches are platform-dependent. They cannot be implemented on HPC systems where the I/O node mapping cannot be easily changed, e.g., BlueGene. Fortunately, our second approach of reallocating compute nodes is more flexible as it has no hardware requirements.

Some studies focus on promoting a job's performance by optimizing the resource allocation strategy. Deveci et al. [35] present a mapping of tasks to processors to reduce parallel applications' communication time. Subramoni et al. [47] further reduce communication overhead by considering network topology information and over-subscription of network links when allocating compute nodes for jobs. Both the topology information and application communication pattern are taking into account the node allocation strategy of later work [48]. However, they do not delve into the communication pattern differences among an application's multiple runs. We extract and validate the communication patterns with realistic traces before using them to guide the node allocation. An extended gang scheduling strategy [49] is proposed to collocate a job's processes and their data by adding different levels of I/O awareness. Qin et al. [50] present an I/O-aware load balance scheme for heterogeneous clusters whose compute nodes are equipped with disks of different capabilities. Herbein et al. [51] propose batch job scheduling techniques that reduce I/O interference between jobs by modeling available bandwidth of network links between each level of the storage architecture. Above work optimizes node allocation strategy by adding resourceawareness. In contrast, our approach does not need monitoring the resource when making node allocation decisions.

# 9 CONCLUSION

In this work, we identify the spatially bursty I/O characteristic on supercomputers by investigating massive I/O traces of two production systems. Spatially bursty I/O, i.e., I/O bursty in the space dimension, is a phenomenon that I/O traffic peaks only originate from a small number of adjacent compute nodes. After examinations, we find that it is mainly caused by the uneven I/O distribution on job processes and the uneven job node distribution on the system. On systems with I/O forwarding layer, an architecture widely adopted by modern supercomputers, spatially bursty I/O will result in load imbalance and underutilization on the I/O nodes. We propose two approaches that both can significantly promote the performance and load balance of I/O forwarding layer, which moreover are suitable for different kinds of platforms. I/O node remapping mechanism can be easily implemented on platforms whose I/O nodes are capable to be mapped to every compute node. Compute node reallocation strategy is suitable for any platform hardware under the premise of extensive investigation and classification of application I/O characteristics. We have deployed the proposed I/O node mapping on a production system for 11 months. It has significantly promoted the load balance and performance of I/O forwarding layer while mitigating I/O interference.

# ACKNOWLEDGMENTS

This work was supported by National Numerical Windtunnel Project of China.

# REFERENCES

- [1] T. Hey et al., The Fourth Paradigm: Data-Intensive Scientific Discovery, vol. 1. Redmond, WA, USA: Microsoft Research, 2009.
- [2] M. Hilbert and P. Lopez, "The world's technological capacity to store, communicate, and compute information," Science, vol. 332, no. 6025, pp. 60–65, 2011.
- [3] C. P. Chen and C.-Y. Zhang, "Data-intensive applications, challenges, techniques and technologies: A survey on big data," Inf. Sci., vol. 275, pp. 314–347, 2014.
- [4] Y. Kim, R. Gunasekaran, G. M. Shipman, D. A. Dillow, Z. Zhang, and B. W. Settlemyer, "Workload characterization of a leadership class storage cluster," in Proc. 5ht IEEE Petascale Data Storage Workshop, 2010, pp. 1–5.
- [5] H. Luu et al., "A multiplatform study of I/O behavior on petascale supercomputers," in Proc. 24th Int. Symp. High-Perform. Parallel Distrib. Comput., 2015, pp. 33–44.
- [6] M. Dorier, S. Ibrahim, G. Antoniu, and R. Ross, "Using formal grammars to predict I/O behaviors in HPC: The omnisc'IO approach," IEEE Trans. Parallel Distrib. Syst., vol. 27, no. 8, pp. 2435–2449, Aug. 2016.
- [7] Q. Koziol et al., High Performance Parallel I/O. Boca Raton, FL, USA: CRC Press, 2014.
- [8] S. Oral et al., "Best practices and lessons learned from deploying and operating large-scale data-centric parallel file systems," in Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal., 2014, pp. 217–228.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:56:54 UTC from IEEE Xplore. Restrictions apply.

- [9] R. Gunasekaran, S. Oral, J. Hill, R. Miller, F.Wang, and D. Leverman, "Comparative I/O workload characterization of two leadership class storage clusters," in Proc. 10th Parallel Data Storage Workshop, 2015, pp. 31–36.
- [10] Y. Liu, R. Gunasekaran, X. Ma, and S. S. Vazhkudai, "Server-side log data analytics for I/O workload characterization and coordination on large shared storage systems," in Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal., 2016, Art. no. 70.
- [11] T. Patel, S. Byna, G. Lockwood, and D. Tiwari, "Revisiting I/O behavior in large-scale storage systems: The expected and the unexpected," in Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal., 2019, Art. no. 65.
- [12] P. Carns et al., "Understanding and improving computational science storage access through continuous characterization," ACM Trans. Storage, vol. 7, no. 3, 2011, Art. no. 8.
- [13] N. Liu et al., "On the role of burst buffers in leadership-class storage systems," in Proc. IEEE 28th Symp. Mass Storage Syst. Technol., 2012, pp. 1–11.
- [14] B. Landsteiner, D. Henseler, and D. Petesch, "Architecture and design of cray DataWarp," in Proc. Cray Users' Group Tech. Conf., 2016.
- [15] Y. Qian et al., "LPCC: Hierarchical persistent client caching for lustre," in Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal., 2019, Art. no. 88.
- [16] S. Oral et al., "End-to-end I/O portfolio for the summit supercomputing ecosystem," in Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal., 2019, Art. no. 63.
- [17] J. E. Garlick, "I/O forwarding on livermore computing commodity linux clusters," Lawrence Livermore National Laboratory (LLNL), Livermore, CA, USA, Tech. Rep. LLNL-TR-609233. 2012.
- [18] N. Ali et al., "Scalable I/O forwarding framework for highperformance computing systems," in Proc. IEEE Int. Conf. Cluster Comput. Workshops, 2009, pp. 1–10.
- [19] TOP500, "Top500 supercomputer sites," 2019. [Online]. Available: http://www.top500.org, TOP500
- [20] M. Xie, Y. Lu, L. Liu, H. Cao, and X. Yang, "Implementation and evaluation of network interface and message passing services for TianHe-1A supercomputer," in Proc. IEEE 19th Annu. Symp. High Perform. Interconnects, 2011, pp. 78–86.
- [21] X. J. Yang, X. K. Liao, K. Lu, Q. F. Hu, J. Q. Song, and J. S. Su, "The TianHe-1A supercomputer: Its hardware and software," J. Comput. Sci. Technol., vol. 26, no. 3, pp. 344–351, 2011.
- [22] A. B. Yoo, M. A. Jette, and M. Grondona, "SLURM: Simple linux utility for resource management," in Proc. Workshop Job Scheduling Strategies Parallel Process., 2003, pp. 44–60.
- [23] C. E. Shannon, "A mathematical theory of communication," ACM SIGMOBILE Mobile Comput. Commun. Rev., vol. 5, no. 1, pp. 3–55, 2001.
- [24] S. Kullback and R. A. Leibler, "On information and sufficiency," Ann. Math. Statist., vol. 22, no. 1, pp. 79–86, 1951.
- [25] Slurm topology guide, 2019. [Online]. Available: https://slurm. schedmd.com/topology.html
- [26] V. Vishwanath et al., "Accelerating I/O forwarding in IBM blue Gene/P systems," in Proc. ACM/IEEE Int. Conf. High Perform. Comput. Netw. Storage Anal., 2010, pp. 1–10.
- [27] J. Liu, Q. Koziol, H. Tang, F. Tessier, and W. Bhimji, "Understanding the I/O performance gap between cori KNL and haswell," Lawrence Berkeley National Lab, 2017.
- [28] X. Liao, L. Xiao, C. Yang, and Y. Lu, "MilkyWay-2 supercomputer: System and application," Front. Comput. Sci. Sel. Publications Chinese Universities, vol. 8, no. 3, pp. 345–356, 2014.
- [29] X. Ji et al., "Automatic, application-aware I/O forwarding resource allocation," in Proc. 17th USENIX Conf. File Storage Technol., 2019, pp. 265–279.
- [30] J. Yu, G. Liu, X. Liu, W. Dong, X. Li, and Y. Liu, "Rethinking node allocation strategy for data-intensive applications in consideration of spatially bursty I/O," in Proc. Int. Conf. Supercomputing, 2018, pp. 12–21.
- [31] B. M. Kettering, A. Torrez, D. J. Bonnie, and D. Shrader, "Lustre and PLFS parallel I/O performance on a cray XE6[R]," Los Alamos National Lab. (LANL), Los Alamos, NM, USA, 2014.
- [32] A. Nisar, W. K. Liao, and A. Choudhary, "Delegation-based I/O mechanism for high performance computing systems," IEEE Trans. Parallel Distrib. Syst., vol. 23, no. 2, pp. 271–279, Feb. 2012.
- [33] C. S. Daley, D. Ghoshal, G. K. Lockwood, and S. Dosanjh, "Performance characterization of scientific workflows for the optimal use of burst buffers," Future Gener. Comput. Syst., vol. 110, pp. 468–480, 2020.

- [34] F. Tessier, V. Vishwanath, and E. Jeannot, "TAPIOCA: An I/O library for optimized topology-aware data aggregation on largescale supercomputers," in Proc. IEEE Int. Conf. Cluster Comput., 2017, pp. 70–80.
- [35] M. Deveci, K. Devine, K. Pedretti, M. Taylor, S. Rajamanickam, and U. Catalyurek, "Geometric mapping of tasks to processors on parallel computers with mech or torus networks," IEEE Trans. Parallel Distrib. Syst., vol. 30, no. 9, pp. 2018–2032, Sep. 2019.
- [36] S. Schlagkamp, R. Ferreira da Silva, W. Allcock, E. Deelman, and U. Schwiegelshohn, "Consecutive job submission behavior at mira supercomputer," in Proc. 25th ACM Int. Symp. High-Perform. Parallel Distrib. Comput., 2016, pp. 93–96.
- [37] IOR HPC benchmark," 2020. [Online]. Available: https://github. com/LLNL/ior
- [38] BTIO, 2020. [Online]. Available: https://www.nas.nasa.gov/ publications/npb.html
- [39] S. Zhang, H. Zhang, and C.-W. Shu, "Topological structure of shock induced vortex breakdown," J. Fluid Mechanics, vol. 639, pp. 343–372, 2009.
- [40] O. Yildiz, M. Dorier, S. Ibrahim, R. Ross, and G. Antoniu, "On the root causes of cross-application I/O interference in HPC storage systems," in Proc. IEEE Int. Parallel Distrib. Process. Symp., 2016, pp. 750–759.
- [41] M. Dorier, G. Antoniu, R. Ross, D. Kimpe, and S. Ibrahim, "CALCioM: Mitigating I/O interference in HPC systems through cross-application coordination," in Proc. IEEE Int. Parallel Distrib. Process. Symp., 2014, pp. 155–164.
- [42] A. Gainaru, G. Aupy, A. Benoit, F. Cappello, Y. Robert, and M. Snir, "Scheduling the I/O of HPC applications under congestion," in Proc. Parallel Distrib. Process. Symp., 2015, pp. 1013–1022.
- [43] K. Ohta, D. Kimpe, J. Cope, K. Iskra, R. Ross, and Y. Ishikawa, "Optimization techniques at the I/O forwarding layer," in Proc. IEEE Int. Conf. Cluster Comput., 2010, pp. 312–321.
- [44] V. Vishwanath, M. Hereld, V. Morozov, and M. E. Papka, "Topology-aware data movement and staging for I/O acceleration on Blue Gene/P supercomputing systems," in Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal., 2011, Art. no. 19.
- [45] J. Yu, G. Liu, X. Li, W. Dong, and Q. Li, "Cross-layer coordination in the I/O software stack of extreme-scale systems," Concurrency Comput. Pract. Experience, vol. 30, 2018, Art. no. e4396.
- [46] J. Yu et al., "Further exploit the potential of I/O forwarding by employing file striping," in Proc. 15th IEEE Int. Symp. Parallel Distrib. Process. Appl., 2017, pp. 322–330.
- [47] H. Subramoni et al., "Design of network topology aware scheduling services for large infiniband clusters," in Proc. IEEE Int. Conf. Cluster Comput., 2014, pp. 1–8.
- [48] Y. Georgiou et al.,"Topology-aware job mapping," Int. J. High Perform. Comput. Appl., vol. 32, pp. 14–27, 2017.
- [49] Y. Zhang, A. Yang, A. Sivasubramaniam, and J. Moreira, "Gang scheduling extensions for I/O intensive workloads," in Proc. Int. Workshop Job Scheduling Strategies Parallel Process., 2007, pp. 183–207.
- [50] X. Qin, H. Jiang, A. Manzanares, X. Ruan, and S. Yin, "Dynamic load balancing for I/O-intensive applications on clusters," ACM Trans. Storage, vol. 5, no. 3, pp. 1–38, 2009.
- [51] S. Herbein et al., "Scalable I/O-aware job scheduling for burst buffer enabled HPC clusters," in Proc. ACM Int. Symp. High-Perform. Parallel Distrib. Comput., 2016, pp. 69–80.

![](_page_13_Picture_44.png)

Jie Yu received the BS, MS, and PhD degrees from the National University of Defense Technology (NUDT), China, in 2011, 2013, 2018, respectively. He is currently a research associate at the Computational Aerodynamics Institute, China Aerodynamics Research and Development Center (CARDC). His current research interests are high peformance I/O, paralell file systems and system monitoring and diagnosis.

![](_page_14_Picture_1.png)

Wenxiang Yang received the BS and MS degrees from the National University of Defense Technologies (NUDT), China, in 2014 and 2016 respectively. He is currently a research assistant at the Computational Aerodynamics Institute, China Aerodynamics Research and Development Center (CARDC). His research interests are high peformance I/O, high peformance interconnects, and system monitoring and diagnosis.

![](_page_14_Picture_3.png)

![](_page_14_Picture_4.png)

![](_page_14_Picture_5.png)

Fang Wang received the BS degree from the National University of Defense Technology (NUDT), China, in 1997, the MS degree from China Aerodynamics Research and Development Center (CARDC) in 2000, and the PhD degree from the National University of Defense Technology, China, in 2017. He is currently a senior engineer and the director at the Computing Center, CARDC, China. His research interests are scientific visualization and high performance computing.

![](_page_14_Picture_7.png)

Dezun Dong received the BS, MS, and PhD degrees from the National University of Defense Technology (NUDT), China, in 2002, 2004, 2010, respectively. He was a visiting scholar with the Department of Computer Science and Engineering, Hong Kong University of Science and Technology, Hong Kong from November 2008 to May 2010. He is currently a professor at the College of Computer, National University of Defense Technology, China. His research interests are on-chip router architecture, adaptive routing algorithms and flow control.

![](_page_14_Picture_9.png)

Yuqi Li received the BS degree from Nanchang University, China, in 2012, and MS degree from Nankai University, China, in 2017. He has worked as an engineer at National Supercomputer Centre in Tianjin (NSCC-TJ) for 7 years. His main research interests are high performance computing, machine learning and system monitoring and diagnosis.

" For more information on this or any other computing topic, please visit our Digital Library at www.computer.org/csdl.

