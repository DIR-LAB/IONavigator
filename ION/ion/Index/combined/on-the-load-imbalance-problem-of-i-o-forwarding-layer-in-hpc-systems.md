# **On the Load Imbalance Problem of I/O Forwarding Layer in HPC Systems**

Jie Yu1 , Guangming Liu1, 3, Wenrui Dong1 , Xiaoyong Li2 , Jian Zhang3 , Fuxing Sun3

1 College of Computer, National University of Defense Technology

2 Academy of Ocean Science and Engineering, National University of Defense Technology

3 National Supercomputer Centre in Tianjin

e-mail: {yujie, liugm, dongwr, zhangjian, sunfx}@nscc-tj.gov.cn sayingxmu@163.com

*Abstract*—**As the computing capability of top HPC systems increases towards exascale, the I/O traffic from tremendous amount of compute nodes have stretched underlying storage system to its limit. I/O forwarding was proposed to address such problem by reducing the number of clients of storage system to a much smaller number of I/O nodes. In this paper, we study the load imbalance problem of I/O forwarding layer, and find that the bursty I/O traffic of HPC applications and the commonly existing rank 0 I/O pattern make the load on I/O nodes highly unbalanced. The application performance is limited if some of the I/O nodes become hot spots while others have little workload to manage. We propose to apportion the heavy I/O workloads of a single I/O node to multiple idle I/O nodes to alleviate the load imbalance. We implement our ideas on an open-sourced I/O forwarding software IOFSL. The preliminary results indicate that our approach can accelerate I/O performance greatly.** 

*Keywords-I/O forwarding; load imbalance; file striping; IOFSL* 

#### I. INTRODUCTION

The rapid development of CPU and multi-core technology enables the computing capability of HPC systems to grow quickly towards exascale. Take the latest top 1 HPC system Sunway TaihuLight as an example, its Linpack performance has arrived 93 petaflops, with more than ten millions of compute cores [1]. However, the performance growth of I/O subsystem in HPC hasn't matched the speed of growth of compute subsystem. Underlying storage systems are becoming incompetent to deal with I/O requests from enormous amount of compute nodes [2].

I/O forwarding was proposed to alleviate the mismatch of I/O and compute performance. In a HPC system with I/O forwarding layer, tremendous amount of compute nodes and storage servers are bridged with a much smaller number of I/O nodes. Each I/O node deals with the I/O requests of a small group of I/O nodes, i.e. 64 compute nodes in the same cabinet, and forwards their requests to storage system. It reduces the I/O concurrency both in I/O nodes and storage servers, and perfectly scales I/O to extreme amount of compute nodes.

However, the I/O traffic of HPC applications are bursty, which makes the load on I/O nodes very unbalanced (detailed in Section III-A). And the commonly existing rank 0 I/O pattern aggravates the load imbalance (detailed in Section III-B). It is a serious waste of precious I/O resources when small number I/O nodes become hot spots while others are only lightly loaded. In this paper, we propose to mobilize multiple I/O nodes to share the heavy workloads of a busy I/O node, so that the aggregate I/O bandwidth of multiple I/O nodes can be exploited. We implement and evaluate our approach on an open-source I/O forwarding software IOFSL [3], and the preliminary results show that the load imbalance problem can be resolved by our approach.

The rest of the paper is organized as follows. We first introduce the background of I/O forwarding in HPC systems, and enumerate several studies that are closely related to our work in Section II. In Section III, we identify the load imbalance problem of I/O nodes by detailing the bursty I/O and rank I/O patterns of HPC applications. We elaborate the design choices and implementation details of our approach in Section IV, and evaluate it in Section V. We conclude our work in Section VI.

#### II. BACKGROUND AND RELATED WORK

#### A. *I/O Forwarding*

I/O forwarding is initially proposed to alleviate the operate system noise on compute nodes of HPC systems. General purpose operate systems like Linux provides mechanisms, such as context switching and process preemption, to ensure low latency of multi-thread program or support multi-user scenario. Meanwhile, it brings serious system noise that can significantly impact application performance. Therefore light weight kernels [4], whose I/O system calls are disabled, are used in compute nodes of HPC systems to reduce system noise. Compute nodes have to forward their I/O requests to dedicated I/O nodes to access data. A typical I/O forwarding architecture is shown in Figure 1.

![](_page_0_Figure_18.png)

Figure 1. I/O forwarding architecture on HPC systems.

The continued growing computing capability of HPC systems has made storage system more and more incompetent to handle extremely amount of clients. Apart from reducing noise in compute nodes, I/O forwarding

perfectly scales I/O to tremendous amount of compute nodes by reducing the number of clients of storage system to the number of I/O nodes. As an I/O node handles requests of multiple compute nodes, it provides an opportunity to rearrange, aggregate and cache I/O requests on the I/O nodes to further reduce the I/O requests sent to storage systems. Therefore, I/O forwarding layer resolves the concurrency problem on storage system, and becomes a standard layer in HPC I/O stack.

### *B. Related Work*

There are plenty of works that optimize I/O forwarding performance with mechanisms like I/O scheduling or data staging [5, 6]. Burst buffer [7] was proposed to buffer large amount of data in the SSDs attached to I/O nodes. Many works have extended burst buffer to form a global temporary storage space [8]. However, these works didn't resolve the load imbalance problem of I/O forwarding layer, and the compute nodes can only communicate with only one I/O node.

Liao et al. [9] proposed delegation-based I/O within ROMIO library. It uses two groups of MPI processes, one group is the processes of applications, and the other is the I/O proxy processes that forward I/O requests for the former group. After receiving the I/O requests, the proxy processes can communicate and exchange data with each other, then it optimize I/O performance like Collective I/O. In contrast, our approach does not need to exchange data between I/O nodes to perform optimization. All data are striped already on the client side.

Cray DVS [10] is the I/O forwarding software of Cray XT systems. It has two different I/O forwarding modes. In its serial mode, the I/O requests of a compute node are forwarded to just one I/O node. In the cluster parallel access mode, a compute node can interact with multiple I/O nodes. Different with our approach, the I/O requests of a same file can only be forwarded to a same I/O node for coherency issues. Although it provides better locality, it can seriously impact I/O performance because it is common that many processes access a single large file in HPC applications.

#### III. LOAD IMBALANCE ON I/O FORWARDING LAYER

## *A. Bursty I/O Workloads*

Bursty I/O is a common I/O pattern observed in HPC applications [11]. A study on the I/O workload of a top HPC system Intrepid shows that, the I/O bandwidth of its storage system are utilized less than 33% for 98% of the time [12]. HPC applications have clearly distinguishable execution phases. In computation dominant phases, compute nodes are busy processing data and communicating intermediate results with each other. In I/O dominant phases, compute nodes are busy writing or reading data from storage systems. A typical example is defensive I/O, i.e. checkpoint and restart, which is used to storing data to protect results from data loss due to system failure. Therefore, I/O nodes are not busy all the time.

I/O workloads are not only bursty in time, but also bursty in space, which means that only a small number of I/O nodes are busy at the same time. A study [13] on multiple HPC platforms shows that, the I/O bandwidth of their storage systems are mainly consumed by a small number of big I/O applications. Almost all big I/O applications have small jobs that running on less than 2K processes. Especially, in a HPC platform called Edison, almost all big I/O applications run on less than 2K processes. Since each compute nodes on Edison has 12 cores, these jobs are running on less than 160 compute nodes. Slurm scheduling system [14] preferentially allocate large bulks of adjacent compute nodes for jobs, therefore it is likely that most of their I/O traffic are forwarded to 3 or 4 I/O nodes, assuming that the ratio of I/O nodes and compute nodes is 1:64.

Based on above analysis, bursty I/O workloads make the I/O nodes very load unbalanced. A small minority of I/O nodes can easily become hot spots, while other I/O nodes have few I/O traffic to process.

#### *B. Rank 0 I/O*

HPC applications mobilize thousands of processes to collaborate with each other for parallel processing via Message Passing Interface (MPI). Each MPI process has a rank ID to identify itself. All rank I/O is an I/O pattern that all processes of an application perform I/O for their own needs, as shown in Figure 2. It is an intuitive way to access data since every process gets their requested data directly.

![](_page_1_Figure_13.png)

Figure 2. A demostration of all rank I/O.

There is another common I/O pattern in scientific applications, rank 0 I/O [15]. Rank 0 I/O is an I/O pattern that only the root process performs I/O. Figure 3 shows an example that demonstrates rank 0 I/O. Scientific applications often use high level I/O library to manage extremely large and complex scientific data collections. However, some of these high level I/O libraries, i.e. netCDF [16], do not support multiple processes parallel accessing data. The root process has to read the data from storage systems, distribute them to all processes for computing, and collect the results back when computation ends. Rank 0 I/O also exists in applications that need perform reduction operations, i.e. adding or sorting, to all the data distributed in the cluster. Root process has to collect data from all the other processes and write them back to storage systems after processing. Rank 0 I/O works well when reading small files like configuration or log files. Its performance is limited when accessing enormous amount of scientific data.

![](_page_2_Figure_0.png)

Rank 0 I/O aggravates the load imbalance of I/O nodes. The I/O node that handles requests of root process has tremendous amount of I/O traffic to deal with, while other I/O nodes that handle requests of other processes have few workload to manage.

#### IV. MOBILIZE MULTIPLE I/O NODES

#### *A. Overview*

The bursty I/O HPC workloads and the commonly existing rank 0 I/O have made I/O nodes very load unbalanced. Some of the I/O nodes can easily become hot spots, while others are lightly loaded. It is necessary to mobilize theses lightly loaded I/O nodes to bear extra I/O workloads of the busy ones. Otherwise, it is a serious waste of precious I/O resources. The potential of I/O forwarding layer cannot be fully realized as well.

Inspired by the commonly used file striping mechanism in parallel file systems, we propose to strip files across a group of I/O nodes, so that they can share the heavy I/O traffic of a single I/O node. The I/O requests of compute nodes are forwarded to multiple I/O nodes, instead of only one, and each I/O node is responsible of different file parts. Compute nodes can take advantage of the aggregate I/O bandwidth of multiple I/O nodes. In the meanwhile the workloads on I/O nodes are balanced.

#### *B. Select I/O nodes*

In HPC systems, each compute node has been mapped with an I/O node statically. Its I/O requests are all forwarded to this I/O node, which we call primary I/O node. Each primary I/O node serves I/O requests of a group of compute nodes. In our approach, we plan to add more I/O nodes to server the requests of a compute node, which we call additional I/O nodes.

After a user submits the job to HPC system, the Slurm scheduling system will allocate appropriate compute nodes for the job according to its requirement. The I/O requests of the processes running on the allocated compute nodes are forwarded to their corresponding statically mapped I/O nodes. Based on the names of allocated compute nodes obtained from Slurm, we can deduct the names of their primary I/O nodes according to the static mappings. The allocated compute nodes can be classified to multiple groups according to their different primary I/O nodes. We select a certain number of additional I/O nodes for each compute node group from the I/O nodes that have not been used by this job. Since the I/O nodes of the same job are likely to handle bursty I/O traffic at the same time point, this method ensures that heavy I/O workloads are apportioned to idle I/O nodes.

There is a potential problem of selecting additional I/O nodes through above method. Every selected additional I/O node has its own statically mapped group of compute nodes to serve. If we allocate extra I/O workloads on them, it may impact the I/O performance of their compute nodes. Fortunately, as depicted in Section III-A, the I/O workloads are bursty both in time and space. Therefore, it is unlikely that a large number of I/O nodes are all busy at the same time. If the I/O phases of multiple applications are staggered from each other, then our approach will gain significant benefits.

#### *C. Implementation*

We decide to implement our approach on an open-source I/O forwarding software IOFSL. IOFSL is a scalable, unified high-end computing I/O forwarding software layer designed by Argonne National Laboratory. It is now widely used for research purpose.

As shown in Figure 4, there are two main components in IOFSL, a client in the compute node side that intercepts and forwards I/O requests of applications, a server in the I/O node side that handles the forwarded I/O requests and access data in the storage system on behalf of compute nodes.

![](_page_2_Figure_14.png)

Figure 4. The software stack of IOFSL.

IOFSL clients communicate I/O requests with IOFSL servers using the ZOIDFS protocol. ZOIDFS is a protocol designed for forwarding I/O requests, which provides a stateless, portable and distributable file handles instead of file descriptors. Applications can pass their I/O requests to IOFSL clients through various interfaces, including ROMIO in MPI-IO, libfuse in FUSE and glibc. IOFSL servers use the client interfaces exposed by back-end storage system to access data. They are servers that handle I/O requests of compute nodes, as well as clients of storage systems that issue I/O requests. IOFSL clients and servers communicate with BMI interconnect abstraction.

We implement file striping on the IOFSL client side. When a client receives an I/O request from an application, it first calculates which I/O node to send it to according to its striping parameters. If this request spans multiple data stripes, client divides it into multiple requests and sends them to different I/O nodes. Therefore, this I/O request can be handled by multiple I/O nodes in parallel, and the single hot spot is eliminated. There is no need to worry about the data coherency in multiple I/O nodes. IOFSL supports multiple I/O nodes accessing the same file. The coherency is handled by the IOFSL servers and the parallel file system clients. Our modification of splitting I/O traffic on the clients will not affect the data coherency.

#### V. PRELIMINARY RESULTS

## *A. Experimental Setup*

We evaluate our approach in Tianhe-1A in National Supercomputer Centre in Tianjin. Each computer node has 2 Intel Xeon X5670 CPU (6 cores, 2.93 GHz) and 24 GB of RAM. As Tianhe-1A has no I/O forwarding infrastructure, we use compute nodes as I/O nodes. To truly reflect the actual I/O forwarding architecture, for each group of compute nodes, we locate the primary I/O node in the same cabinet, and locate the additional I/O nodes in other cabinets. We use 32 object storage servers (OST) in a Lustre file system. Each OST's peak bandwidth is about 200 MB/s. Files are distributed in all these OSTs with stripe size 1 MB.

#### *B. IOR Benchmark*

IOR is a benchmark widely used to evaluate parallel I/O performance of large scale storage systems. In order to evaluate the benefits brought to rank 0 I/O, we run an IOR process on a compute node and compare its I/O bandwidth with and without our optimization. The results are shown in Figure 5. In the figure, the bandwidth with only 1 I/O node is the performance tested without our optimization. We apportion the original I/O workloads of the single I/O node to multiple I/O nodes. In the test we use different numbers of I/O nodes for each compute node.

As can be seen from Figure 5, IOR can utilize more processes on more I/O nodes to access data in Lustre after being optimized with our approach. The heavy workloads on a single I/O node are apportioned to multiple I/O nodes, which greatly enhances the aggregate read and write bandwidth. The more I/O nodes are utilized, the better the performance is promoted. The results indicate that our approach can significantly accelerate I/O performance of applications when a single I/O node becomes the bottleneck.

#### *C. Compare with Cray DVS*

We compare our approach with Cray DVS in this section. As Cray DVS is not open-sourced, we developed a version of IOFSL that emulates the architecture of Cray DVS for demonstration. In this version of IOFSL, a compute node can also interact with multiple I/O nodes. The clients on the compute nodes issue their requests of different files to different I/O nodes. Different with our approach, the files are located in different I/O nodes determined by the hash value of their file paths. Therefore, when multiple compute nodes access the same file, their requests are all sent to the same I/O nodes.

![](_page_3_Figure_10.png)

Figure 5. IOR performance with different number of I/O nodes.

We test the performance with two different I/O patterns, N-1 pattern that N processes access 1 file, and N-N pattern that each of the N processes accesses its own independent file. We run 12 IOR processes on each of 8 compute nodes, and there are 4 I/O nodes for each compute node.

From the results in Figure 6, we can find that their performance is about the same with N-N pattern. The reason is that, in Cray DVS, files are distributed in all I/O nodes almost uniformly since the hash function is consistent. Therefore our approach and DVS can both utilize the aggregate bandwidth of these I/O nodes. However, with N-1 pattern that all processes access a large file, the file is only located in a single I/O nodes in Cray DVS. On the contrary, our approach can still obtain high bandwidth since the large file is striped across multiple I/O nodes.

![](_page_3_Figure_14.png)

Figure 6. Compare with Cray DVS with N-N and N-1 patterns.

#### VI. CONCLUSION

We study the load imbalance problem of I/O forwarding layer in HPC systems, and find that bursty I/O workload and commonly existing rank 0 I/O pattern can make the workload on I/O nodes highly unbalanced. To address the load imbalance problem on I/O nodes, we propose to mobilize multiple I/O nodes to share the heavy workloads of a single I/O node. We carefully select a group of I/O nodes to bear extra I/O workload, and employ file striping on them. So that clients can make full use of the aggregate bandwidth of multiple I/O nodes and the load on I/O nodes are more balanced. We test our ideas on a popular I/O forwarding software IOFSL. The preliminary results show that our approach outperforms Cray DVS, and can accelerate application performance significantly.

## ACKNOWLEDGMENT

This work was supported by the National Key Research and Development Program of China (Grant No. 2016YFB0200402), and the National Natural Science Foundation of China (Grant No. 61502511).

#### REFERENCES

- [1] "Top500 supercomputer sites," http://www.top500.org.
- [2] W. Hu, G.-m. Liu, Q. Li, Y.-h. Jiang, and G.-l. Cai, "Storage wall for exascale supercomputing," Journal of Zhejiang University-SCIENCE, vol. 2016, pp. 10–25, 2016.
- [3] N. Ali, P. Carns, K. Iskra, D. Kimpe, S. Lang, R. Latham, R. Ross, L. Ward, and P. Sadayappan, "Scalable i/o forwarding framework for high-performance computing systems," in IEEE International Conference on CLUSTER Computing and Workshops, 2009, pp. 1– 10.
- [4] S. M. Kelly and R. Brightwell, "Software architecture of the light weight kernel, catamount," Cray User Group, pp. 16–19, 2005.
- [5] V. Venkatesan, M. Chaarawi, Q. Koziol, and E. Gabriel, "Compactor: Optimization framework at staging i/o nodes," in Parallel & Distributed Processing Symposium Workshops, 2014, pp. 1689–1697.
- [6] K. Ohta, D. Kimpe, J. Cope, K. Iskra, R. Ross, and Y. Ishikawa, "Optimization techniques at the i/o forwarding layer," in IEEE

International Conference on CLUSTER Computing, 2010, pp. 312– 321.

- [7] N. Liu, J. Cope, P. Carns, C. Carothers, R. Ross, G. Grider, A. Crume, and C. Maltzahn, "On the role of burst buffers in leadership-class storage systems," in Mass Storage Systems and Technologies (MSST), 2012 IEEE 28th Symposium on. IEEE, 2012, pp. 1–11.
- [8] T. Wang, K. Mohror, A. Moody, K. Sato, and W. Yu, "An ephemeral burst-buffer file system for scientific applications," in Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis. IEEE Press, 2016, p. 69.
- [9] A. Nisar, W. K. Liao, and A. Choudhary, "Delegation-based i/o mechanism for high performance computing systems," IEEE Transactions on Parallel & Distributed Systems, vol. 23, no. 2, pp. 271–279, 2012.
- [10] S. S and W. D, "Cray dvs: Data virtualization service," in Proc. Cray Users Group Technical Conference (CUG), 2008.
- [11] Y. Kim, R. Gunasekaran, G. M. Shipman, D. A. Dillow, Z. Zhang, and B. W. Settlemyer, "Workload characterization of a leadership class storage cluster," in Petascale Data Storage Workshop (PDSW), 2010 5th. IEEE, 2010, pp. 1–5.
- [12] P. Carns, K. Harms, W. Allcock, C. Bacon, S. Lang, R. Latham, and R. Ross, "Understanding and improving computational science storage access through continuous characterization," ACM Transactions on Storage (TOS), vol. 7, no. 3, p. 8, 2011.
- [13] H. Luu, M. Winslett, W. Gropp, R. Ross, P. Carns, K. Harms, M. Prabhat, S. Byna, and Y. Yao, "A multiplatform study of i/o behavior on petascale supercomputers," in Proceedings of the 24th International Symposium on High-Performance Parallel and Distributed Computing. ACM, 2015, pp. 33–44.
- [14] A. B. Yoo, M. A. Jette, and M. Grondona, "Slurm: Simple linux utility for resource management," in Workshop on Job Scheduling Strategies for Parallel Processing. Springer, 2003, pp. 44–60.
- [15] Q. Koziol et al., High performance parallel I/O. CRC Press, 2014.
- [16] R. Rew and G. Davis, "Netcdf: an interface for scientific data access," IEEE computer graphics and applications, vol. 10, no. 4, pp. 76–82, 1990.

