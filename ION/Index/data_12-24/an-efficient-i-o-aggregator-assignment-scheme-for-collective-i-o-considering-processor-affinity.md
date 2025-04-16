# **An Efcient I/O Aggregator Assignment Scheme for Collective I/O Considering Processor Afnity**

Kwangho Cha†‡ and Seungryoul Maeng†

†*Department of Computer Science, Korea Advanced Institute of Science and Technology, Daejeon, KOREA* ‡*Supercomputing Center, Korea Institute of Science and Technology Information, Daejeon, KOREA* {*khocha, maeng*}*@camars.kaist.ac.kr*

*Abstract***—As the number of processes in parallel applications increases, the importance of parallel I/O is also emphasized. Collective I/O is the specialized parallel I/O which provides the function of single-le-based parallel I/O. Collective I/O in popular message-passing interface (MPI) libraries follows a two-phase I/O scheme, in which the particular processes, namely I/O aggregators, perform important roles by engaging communications and I/O operations. Although there have been many previous works to improve the performance of collective I/O, it is hard to nd a study about an I/O aggregator assignment considering multi-core architecture. Nowadays, many HPC systems use the multi-core system as a computational node. Therefore, it is important to understand the characteristics of multi-core architecture, such as processor afnity, in order to increase the performance of parallel applications. In this paper, we discovered that the communication costs in collective I/O were different according to the placement of I/O aggregators, where the computational nodes consisted of multicore system and each node had multiple I/O aggregators. We also proposed a modied collective I/O scheme, in order to reduce the communication costs of collective I/O, by proper placement of I/O aggregators. The performance of our proposed scheme was examined on a Linux cluster system and the result demonstrated performance improvements in the range of 7.08% to 90.46% for read operations and 20.67% to 90.18% for write operations.**

*Keywords***-Collective I/O; Parallel I/O; Processor Afnity;**

#### I. INTRODUCTION

Scientic applications that run on high-performance computing (HPC) systems require not only heavy computations but also a large number of le-I/O. Many parallel programming paradigms also provide various I/O methods for scientic applications and previous studies [1], [2], [3] demonstrate the importance of single-le based parallel I/O, especially collective I/O. In order to access a single le simultaneously, multiple processes in the same parallel application use collective I/O1.

The message-passing interface (MPI) which is one of the most famous parallel programming library has collective I/O interface. Collective I/O in MPI follows the two-phase I/O scheme that consists of an I/O phase and a data exchange phase [4]. In the two-phase I/O, the specialized process called I/O aggregator is engages in the both phases. In other words, because the role of I/O aggregator is to collect or distribute I/O data to other clients, collective I/O performance can be affected by the ability of I/O aggregator.

Although there have been many studies on improving the collective I/O performance, many of them have focused on I/O phase issues or le system related topics such as buffering, caching, locking, and so on. It is, however, difcult to locate previous studies on collective I/O in multicore based systems in which each node has multiple numbers of I/O aggregators.

The goal of this study is to discover a relationship between the placement of I/O aggregators in each node and the performance of collective I/O. We also propose an efcient I/O aggregator assignment method that reduces the communication costs in collective I/O.

Multi-core systems have multi-level structure composed of cores, sockets (or chips) and so on2. Because a program's performance depends on which cores (or memories) are assigned to the program, users can dene resource afnity for their programs [7], [8], [9]. In this paper, since we have been focused on the location of I/O aggregators, we consider only processor afnity. In order to identify a link between the performance of collective I/O and processor afnity, we have measured the performance of collective I/O with varying processor afnity rules. The result of the experiment demonstrated that when I/O aggregators were distributed well among sockets (or chips), it was possible to achieve good communication performance of collective I/O.

Processor afnity rules, however, seem to be selected by considering the performance of major routines such as computations rather than that of collective I/O of a given program. In other words, even though an afnity rule guarantees good program performance, it is not always good for collective I/O. This is the reason why we modied collective I/O routines to regulate the location of I/O aggregators even though an inadequate afnity rule for collective I/O is selected.

<sup>1</sup>More strictly speaking, processes in the same communicator can use collective I/O.

<sup>2</sup>For example, IBM Power 595 system having 64 cores consists of 8 processor books. Each processor book has 4 multi-chip module(MCM)s and each MCM is equipped with a dual core processor [5], [6].

|  | Serial I/O | Multi-le based Parallel I/O | Single-le based Parallel I/O |
| --- | --- | --- | --- |
| Denition | Only one process performs I/O | All processes perform I/O | All processes perform I/O |
|  | on behalf of all processes. | with their own les. | with a single shared le. |
| Advantage | Simple and intuitive | Simple and good performance | Preserve the canonical order of structured data |
|  |  | No consistency overhead |  |
| Disadvantage | Bottleneck in the memory of the process performing I/O | Many les | High consistency overhead |
|  |  | The overhead of managing | Additional procedures such as |
|  |  | metadata3 | managing derived data types |
|  |  | Only the same number of |  |
|  |  | processes can use les4 |  |
|  |  | Requires post-processing |  |

Table I: Comparison of I/O methods for parallel applications.

It is true that only some processes can participate in collective I/O by dening a new communicator or splitting an existing communicator. We, however, think that in this case, independent I/O can be used instead of collective I/O. Furthermore, we believe that the performance of collective I/O which are related with all processes is much important than that of collective I/O caused by some processes. Thus, in this paper, it was assumed that all processes participate in collective I/O.

According to the recent report [10], as the performance of parallel le systems increases, it is possible to stably control the concurrent I/O requests of many clients to a shared le to a certain degree. In collective I/O, only I/O aggregators participate in le-I/O. All of this amounts to saying that using the multiple I/O aggregators may result in increased le-I/O performance if there is a powerful parallel le system, We assume that there are multiple I/O aggregators in a node; MPICH, a popular MPI-IO implementation, also provides multiple I/O aggregators per node. File access method of a program depends on the selected programming language [11]. In this paper, because we used C language, it was assumed that a le is stored in row-major order.

Finally, the experiments on a Linux cluster system conrm that our proposed scheme improves the performance of collective I/O. The preliminary performance measurements show that, using the proposed scheme, the read operations are over 7% faster and the write operations are over 20% faster than those operations of the original MPI implementation.

This paper is organized as follows. The previous research on parallel I/O, including collective I/O, and processor afnity is summarized in Section II. Section III presents the issue of collective I/O considering processor afnity and the primary concept of our I/O aggregator assignment scheme. The performance measurements are described in Section IV. Finally, the conclusions are presented in Section V.

#### II. RELATED WORKS

## *A. MPI-IO*

Scientic applications can select the proper le-I/O method among current available techniques as explained in Table I [1], [2], [3]. The advantage of each method is simplicity, good performance, and efcient management. Although some users will continue to use serial I/O or multi-le based parallel I/O, as the number of nodes in a system increases, the drawbacks of these methods cause serious performance problems. This is why previous studies of parallel I/O have focused and insisted on single-le based parallel I/O.

The message passing interface (MPI), the most common parallel programming library, also denes the set of interfaces for single-le based parallel I/O, namely MPI-IO. MPI-IO has been provided by various types of MPI implementations such as MPICH, LAM MPI, HP MPI, NEC MPI, SGI MPI, IBM MPI [12], and so on. MPI-IO has two types of le access functions: independent I/O and collective I/O. In particular, collective I/O enables multiple processes in the same parallel job to simultaneously access a shared le. In order to perform concurrent I/O accesses, collective I/O requires internal collaboration with other processes.

It is well known that many scientic applications generate I/O requests for non-contiguous data. In order to handle a huge number of tiny data chunks, two-phase I/O [11], diskdirected I/O [13], and server-directed collective I/O have been proposed.

Many popular MPI libraries, such as MPICH2 and MVA-PICH2, are equipped with an MPI-IO implementation called ROMIO and collective I/O in ROMIO is based on twophase I/O scheme [11]. In two-phase I/O, because only I/O aggregators can access the portion of the shared le, total workload of all processes is divided and assigned to the I/O aggregators. In case of read operations, I/O aggregators read data from the shared le and then distribute them to other

<sup>3</sup>For the IBM GPFS, generating new les under the same directory causes serious performance degradation [2].

<sup>4</sup>If an application uses checkpoint les, the application must be restarted with the same number of processes as when the checkpoint les were produced.

![](_page_2_Figure_0.png)

Figure 1: Example of two-phase I/O. (a) A 8×4 array is assigned to 8 processes, and each process has a 2×2 sub array. The element size within the sub array is 8 bytes and it is assumed that two processes, P0 and P4, are selected as I/O aggregators. Each I/O aggregator manages the data of the other two client processes which have the same le domain. The collective buffer size is 16 bytes and the array is written in row-major order. (b) The size of whole access region is 256 bytes and that of each I/O aggregator's le domain is 128 bytes. Because the collective buffer size is 16 bytes, collective I/O requires 8 operation steps.

client processes. On the contrary, I/O aggregators collect I/O data to be stored from the clients and then write them to the shared le, for write operation. Figure 1 shows an example of two phase I/O [3], [11].

### *B. Collective I/O Improvements*

In this sub-section, previous studies on improving the performance of collective I/O are introduced. Nitzberg and Lo suggested collective buffering in order to generate optimized I/O requests [14]. This approach rearranges the data in each node before issuing the I/O operations. Active buffering [15] was used for improving collective write performance. When the rst collective write operation is issued, it generates an active buffering space and an I/O thread. For the subsequent write operations, the I/O thread performs the write-behind. In case of a single-le-based parallel I/O, parallel processes tend to refer the same le. Client-side le caching regards each client's I/O requests are related and distributes the cache metadata and local cache pages across the processes

![](_page_2_Figure_5.png)

Figure 2: Example of the computational node with multiple CPU cores. (a) IBM Power 595 system [6]. (b) Texas Advanced Computing Center (TACC) Ranger cluster system [8].

[16], [17]. Unlike POSIX, because atomic MPI-IO operations should manage the overlapping region, such as ghost cells, Liao et al. suggested process rank ordering and graph coloring [18]. Although the original two-phase I/O divides the le domain evenly, most le systems' lock granularity is stripe size or le block size not byte size. Therefore, the partitioned le domain does not t to the lock boundaries and it causes the serious lock overhead. Liao and Choudhary suggested new partitioning scheme considering the lock boundaries [3].

#### *C. Processor Afnity*

According to the TOP500 most powerful supercomputer list, many modern supercomputers are classied into multicore cluster systems that consist of many computational nodes with several CPU cores [19]. The computational nodes have multi-level structure of processor unit and several kinds of communications such as intra-socket, inter-socket, internode and so on, as in Fig. 2 [5], [6], [7], [8].

In such systems, process afnity rules specify the mapping between processes to cores and it is well known that they affect the overall performance of MPI applications [7]. In Linux cluster systems, the *numactl* command describes process afnity rules and IBM AIX system uses mcm *afnity options* keyword to specify those rules [8], [9].

![](_page_3_Figure_0.png)

Figure 3: Breakdown of MPI *File write* all. We timed the collective write operation using MPE Logging function. 16 processes generated a 1 GB shared le. Write contig means le I/O time. W Exch data is the data exchange time.

# III. COLLECTIVE I/O CONSIDERING PROCESSOR AFFINITY

In this section, the background and motivation behind our study is introduced. We also explain the concept of collective I/O considering processor afnity and how it affects the performance of collective I/O.

#### *A. Motivation*

As mentioned in the above sections, collective I/O in MPICH is based on two-phase I/O. During the data exchange phase, I/O aggregators gather or distribute the I/O data to multiple client processes. They also participate in I/O operations during the I/O phase.

As shown in Fig. 3, each phase in two-phase I/O was timed in a cluster system. The results showed that the I/O phase and the data exchange phase are the main timeconsuming processes of collective I/O. In this study, we tried to reduce the communication costs by considering processor afnity because the combination of communications that occur in each computational node will be changed according to processor afnity.

#### *B. Processor Afnity for Collective I/O*

As explained in the previous section, we assume each computational node has multiple I/O aggregators. MPICH also supports multiple numbers of I/O aggregator per node by specifying the *romio-hints* le. For example, *'cb cong list *:2'* describes each node has two I/O aggregators

The current collective I/O implementation in MPICH selects the processes having the lowest process ID in each node as I/O aggregators. In such circumstance, I/O aggregator's communication behavior can be affected by afnity rule. For the better understanding, let us consider the following example in Fig. 4. It draws a distribution of an 8×4 array onto 32 processes in two computational nodes (or machines) and each node has 16 processors. Because it also assumes each node has four I/O aggregators, there are 8 I/O

![](_page_3_Figure_10.png)

Figure 4: Example distribution of an 8×4 array onto 32 processes.

![](_page_3_Figure_12.png)

Figure 5: Example of communication behaviors in *node 0*. The rectangles represent the sockets and the arrows between the sockets indicate inter-socket communication. The arrows in the rectangles are intra-socket communications. The number on the arrows indicates the number of communications. The number of I/O aggregators per node(= α) is four and the circles in the sockets are I/O aggregators.

aggregators, P0, P1, P2, P3, P16, P17, P18, and P19. The size of aggregate access range is α · β and that of each I/O aggregator's le domain is (α·β) 8 . In other words, when a collective I/O operation is issued, it reads or writes α · β bytes and each I/O aggregator handles (α·β) 8 bytes. In case of *node 0*, P0 and P1 handle I/O requests issued by P0 to P7 while P2 and P3 are in charge of I/O requests from P8 to P15. During the data exchange phase, P0 and P1 have to communicate with from P0 to P7 and they use intra-socket or inter-socket communications according to their locations.

Like TACC Ranger cluster system, if a computational node uses four quad-core processors such as SUN blade x6400, afnity rule determines the location of each I/O aggregator as in Fig. 5. It shows two kinds of afnity rule which can be applied to manage I/O requests of the above given example in Fig. 4. The accumulated method rst assigns the processors in the same socket (or chip) to an application, until there are available processors in the socket.

Table II: Expected communication costs of Fig. 5. In view of the communication behavior, we counted the number of ingress and egress communications on each socket. Because SUN blade x6400 has asymmetric inter-connection topology, *socket 0* and *socket 3* in Fig. 5 have a 2-hop distance. We, however, counted the number of conceptual communications for simple expectation.

|  | socket 0 socket 1 socket 2 socket 3 |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
|  | Inter- Inter- Inter- Intra- Inter- socket socket socket socket socket socket socket socket | Intra- | Intra- |  | Intra |
| Accumulated | 24 8 8 8 | 6 | 0 | 0 | 0 |
| Distributed | 12 12 12 12 | 1 | 1 | 2 | 2 |

If all the processors in the socket are not available, then the processors in other sockets will be used as in Fig. 5(a). On the other hand, the distributed method uses the processors across all sockets in round-robin manner as in Fig. 5(b). We also can get expected communication costs of data exchange phases in *node 0* as in Table II.

Although the two afnity rules have the same aggregate number of intra-socket and inter-socket communications in a node, the numbers of communications managed by each socket are different. Considering the communications are performed simultaneously during the data exchange phase, the amount of communications on a hot spot socket will affect the communication performance. This is the reason why we believe the distributed method is more suitable for collective I/O and the results of performance evaluation in the following section validates our prediction.

### *C. New I/O Aggregator Assignment Scheme*

Before introducing the performance of each afnity rule, we explain our new I/O aggregator assignment scheme. As mentioned in the previous sub-section, if we choose the distributed method for processor afnity, reduced communication costs of the hot spot socket will improve the collective I/O performance. Although the distributed method seems to be useful for collective I/O, it may cause performance degradation to other routines such as communications or computations. In other words, if an MPI program communicates with neighbor processes frequently, it is recommended to use the accumulated method for processor afnity but it is not good for collective I/O.

When MPICH decides which processes will be I/O aggregators, MPICH selects the adjacent processes regardless of processor afnity. This makes I/O aggregators are located in the same socket with high probability under the accumulated afnity rule. We modied the way of the collective I/O routine in MPICH which appoints I/O aggregators. Although MPICH don't know the exact architecture of a given multicore system, under the accumulated method, it is possible to prevent letting I/O aggregators in the same socket by arranging them at regular intervals as in Fig. 6.

![](_page_4_Figure_7.png)

Figure 6: The concept of new I/O aggregator assignment scheme. All the cases assume there are two I/O aggregators in each node(α = 2). The rounded rectangles represent the nodes and the shaded rectangles indicate I/O aggregators.

![](_page_4_Figure_9.png)

Figure 7: Communication behaviors of collective I/O using our proposed scheme.

Figure 6 illustrates there is an MPI program using 20 processes and three nodes are assigned to the program. If it is dened to use two I/O aggregators per node, the original MPICH selects P0, P1, P8, P9, P16, and P17 as I/O aggregators. Unlike the original MPICH, our proposed scheme rst calculates the stride factor, si for each *node i*. After selecting an I/O aggregator, it skips si processes and the following process is chosen as the next I/O aggregator for *node i* and iterates the procedure until *node i* has the predened number of I/O aggregators. Consequently, it selects P0, P4, P8, P12, P16, and P18 as I/O aggregators. The stride factor, si is obtained by noting that si = Ni α − 1, where Ni is the total number processes in *node i* and α is the predened number of I/O aggregators per node. With the same condition in sub-section III-B, Fig. 7 shows the communication behavior of collective I/O using our proposed scheme. It gives an evidence that our scheme can generate a balanced communication workload for each socket; there are 8 inter-socket and 3 intra-socket communication requests for each socket.

![](_page_5_Figure_0.png)

Figure 8: Data exchange costs of collective I/O using our proposed scheme and original implementation. New Acc. means the result form our modied scheme under the accumulated afnity rule. Org Dist. and Org Acc. indicate the outputs of the original MPI-IO implementations with the distributed and the accumulated afnity rule respectively. Each data represents the average value of 30 trials.

#### IV. PERFORMANCE EVALUATION

In this section, we analyze the performance of our proposed scheme comparing with the original approach. All experiments in this paper were performed with the Tachyon cluster system5. The cluster system has 188 computational nodes and each is connected via the InniBand network. It uses the same computational nodes which were used by the TACC Ranger cluster system. Table III shows the specications of the Tachyon cluster system.

#### *A. Data Exchange Costs*

We rst evaluated the communication performance of the data exchange phase. In the rst test6, an 8×4 array was distributed to 32 processes, which wrote and read a 2 GB le. The second test handled an 8×8 array and a 4GB le with 64 processes. In order to focus on the data exchange

Table III: Specications of the Tachyon cluster system.

| Hardware |  |
| --- | --- |
| CPU | AMD Opteron 2.3 GHz |
| Number of nodes | 188 |
| Number of CPU cores | 3008 |
| No. of CPU cores/nodes | 16 |
| Memory | 32GB/node |
| Interconnection network | InniBand 4× DDR |
| Software |  |
| OS | CentOS 4.6 |
| MPI | MVAPICH2 1.4 |
| File System | Lustre 1.6.6 |
| Queue Scheduler | SGE 6.1u5 |

phase itself, the execution time excluding the le I/O phase was measured. Because we also tried to identify a link between the performance of collective I/O and the number of I/O aggregators, we measured the time with varying the number of I/O aggregators per node,α. Figure 8 shows the experimental results of the tests.

<sup>5</sup>This is KISTI's fourth supercomputer and it is ranked at 130 in the list of TOP500 most powerful supercomputers published in June 2008 [19]. 6The MPI Tile IO benchmark was used [20].

When the number of I/O aggregator per node is one, the modied method and the original MPI-IO implementation with two afnity rules select the same process as I/O aggregator. This is the reason that Fig. 8(a) shows very similar results. As in Fig. 8(b) to 8(d), our proposed scheme reduces the communication costs noticeably when a node has multiple I/O aggregators. Figure 8 also shows that the original scheme with the distributed afnity rule is effective to decrease the communication time where the number of I/O aggregators per node is greater than two.

Unlike read operation, because write requires additional routines such as *post write* and checking for *read modify write*, it is natural that write takes more time than read. One of the interesting things, however, is when there are multiple I/O aggregators in a node and the accumulated afnity rule is selected, the read operation takes more time than the write. In order to nd out the reason of this phenomenon, we conducted additional experiments for understanding the communication costs itself. During the data exchange phase, all processes participate in asynchronous communications repeatedly. We mimicked the behavior of these asynchronous communications in data exchange phase where the number of I/O aggregator per node is two and message size is 1MB. Figure 9 shows the result of these additional experiments under the accumulated afnity rule. The two communication patterns represent write and read respectively. Although two communications handle the same amount of message, they have different execution time. Furthermore, as the number of iteration increase, communications for read takes more time. We believe this is the main reason why data exchange phase for read operation under the accumulated afnity rule takes more time. We also plan to identify the cause of why the two asynchronous communications have different performance in the future work.

#### *B. Collective I/O Performance*

In addition to the data exchange costs explained in the previous sub-section, the performance of entire collective I/O was measured. Figure 10 shows the results of two tests with a lustre le system which using 8 OSTs.

As mentioned in the previous section, our proposed scheme modies a way of selecting I/O aggregators and it requires additional computations. In spite of the overhead, it reduces the communication costs well and shows the best performance. Under the accumulated afnity rule, the performance improvements between our scheme and the original MPI-IO are approximately 7.08% to 90.46% for the read operation and 20.67% to 90.18% for the write operation.

Comparing with the result of the data exchange costs, there are interesting considerations:

- 1) Generally, while the original scheme with the distributed afnity rule showed slightly improved data
![](_page_6_Figure_7.png)

Figure 9: Communication patterns for write and read and their communication time. (a) Pattern1 represents write operation. (b) Pattern 2 represents read operation. The rounded rectangles indicate sockets (or chips). (c) Asynchronous communication time of (a) and (b).

exchange performance, its collective I/O performance was conspicuously improved.

- 2) Especially, when the number of I/O aggregators per node was two, although the data exchange performance of the original scheme with two afnity rules showed the similar result, collective I/O performance of the original scheme with the distributed afnity rule was improved signicantly.
We believe they are evidence that the afnity rule also affects the performance of I/O phase and our modied scheme and the distributed afnity rule are helpful to increase the I/O phase performance. Under the accumulated afnity rule, because some sockets (chips) are crowed with I/O aggregators, the I/O requests from I/O aggregators can cause bottleneck in those sockets. We believe, however, it is possible to use our proposed scheme or the distributed rule, for mitigating the bottleneck problem at the sockets.

## V. CONCLUSION

As the size and scale of parallel applications increase, the importance of collective I/O is also emphasized. Considering that supercomputer systems use multi-core systems as unit

![](_page_7_Figure_0.png)

Figure 10: Performance of entire collective I/O with 8 OSTs. Each data represents the average value of over 50 trials.

nodes and they have high-performance parallel le systems, using multiple I/O aggregators per node is helpful to improve the performance of collective I/O. Although processor afnity rules affect the performance of applications on multi-core systems, the study about their inuence on collective I/O is hard to nd. In this study, we identied a link between the collective I/O performance and the afnity rule.

We measured the performance under the two afnity rules and the results showed that the distributed afnity rule which puts I/O aggregators in the different sockets is good for not only the data exchange phase but also the I/O phase. Because there may be some applications which can't use the distributed afnity rule, we made new collective IO routines for I/O aggregator assignment which can be used under the accumulated afnity rule. The experimental results showed that the performance improvements using our proposed scheme were in the range of 7.08% to 90.46% for the read operation and 20.67% to 90.18% for the write operation. We plan to expand this research to include various conditions such as the ways of data distribution, hardware architectures, and so on.

#### REFERENCES

- [1] Hongzhang Shan, and John Shalf, "Using IOR to Analyze the I/O performance for HPC Platforms," in Cray Users Group Meeting(CUG) 2007, Seattle, Washington, May 7-10, 2007.
- [2] Zhao Zhang, Allan Espinosa, Kamil Iskra, Ioan Raicu, Ian Foster, and Michael Wilde, "Design and Evaluation of a Collective IO Model for Loosely Coupled Petascale Programming," in Proc. of the ACM/IEEE SC08 Workshop on Many-Task Computing on Grids and Supercomputers, pp. 1∼10, Nov. 2008.
- [3] Wei-keng Liao, and Alok Choudhary, "Dynamically Adapting File Domain Partitioning Methods for Collective I/O based on Underlying Parallel File System Locking Protocols," in Proc. of the 2008 ACM/IEEE conference on Supercomputing, Article no. 3, Nov. 2008.
- [4] Rajeev Thakur, William Gropp, and Ewing Lusk, "Data Sieving and Collective I/O in ROMIO," in Proc. of the 7th Symposium on the Frontiers of Massively Parallel Computation, pp. 182∼189, IEEE Computer Society Press, Feb. 1999.
- [5] H. Q. Le, W. J. Starke, J. S. Fields, F. P. O'Connell, D. Q. Nguyen, B. J. Ronchetti, W. M. Sauer, E. M. Schwarz, and M. T. Vaden,, "IBM POWER6 microarchitecture," in

IBM Journal of Research and Development, vol. 51, no. 6, pp.639∼662, Nov. 2007.

- [6] IBM Power 595 Technical Overview and Introduction, Retrieved Feb. 10, 2011, from http://www.redbooks.ibm.com/redpapers/pdfs/redp4440.pdf
- [7] Chi Zhang , Xin Yuan, and Srinivasan, A., "Processor afnity and MPI performance on SMP-CMP clusters," in Proc. of the IEEE International Symposium on Parallel and Distributed Processing, Workshops and Phd Forum (IPDPSW), April 2010.
- [8] TACC Ranger User Guide, Retrieved Feb. 10, 2011, from http://services.tacc.utexas.edu/index.php/ranger-user-guide
- [9] IBM LoadLeveler for AIX 5L and Linux V3.3.1 Using and Administering, Retrieved Feb. 10, 2011, from http://publib.boulder.ibm.com/epubs/pdf/am2ug303.pdf
- [10] Julian Borrill, Leonid Oliker, John Shalf, Hongzhang Shan, and Andrew Uselton, "HPC global le system performance analysis using a scientic-application derived benchmark," in Parallel Computing, vol. 35, no. 6, pp. 358∼373, Elsevier Science Publishers B. V., June 2009.
- [11] Rajeev Thakur, and Alok Choudhary, "An Extended Two-Phase Method for Accessing Sections of Out-of-Core Arrays," in Scientic Programming, vol. 5, no. 4, pp. 301∼317, 1996.
- [12] Jean-Pierre Prost, Richard Treumann, Richard Hedges, Bin Jia, and Alice Koniges, "MPI-IO/GPFS, an optimized implementation of MPI-IO on top of GPFS," in Proc. of the 2001 ACM/IEEE conference on Supercomputing, Nov. 2001.
- [13] David Kotz, "Disk-directed I/O for MIMD multiprocessors," in ACM Transactions on Computer Systems, vol. 15, no. 1, pp.41∼74, Feb. 1997.
- [14] Bill Nitzberg, and Virginia Lo, "Collective Buffering: Improving Parallel I/O Performance," in Proc. of the IEEE International Symposium on High Performance Distributed Computing, pp. 148∼157, Aug. 1997.
- [15] Xiaosong Ma, MarianneWinslett, Jonghyun Lee, and Shengke Yu, "Improving MPI-IO Output Performance with Active Buffering Plus Threads," in Proc. of the International Parallel and Distributed Processing Symposium, Apr. 2003.
- [16] Wei-Keng Liao, Kenin Coloma, Alok Choudhary, and Lee Ward, "Cooperative Client-Side File Caching for MPI Applications," International Journal of High Performance Computing Applications, vol. 21, no. 2, pp. 144∼154, May 2007.
- [17] Wei-keng Liao, Avery Ching, Kenin Coloma, Arifa Nisar, Alok Choudhary, Jacqueline Chen, Ramanan Sankaran, and Scott Klasky, "Using MPI File Caching to Improve Parallel Write Performance for Large-Scale Scientic Applications," in Proc. of the 2007 ACM/IEEE conference on Supercomputing, Article no. 8, Nov. 2007.
- [18] Wei-keng Liao, Kenin Coloma, Alok Choudhary, Lee Ward, Eric Russell, and Neil Pundit, "Scalable Design and Implementations for MPI Parallel Overlapping I/O," in IEEE Transactions on Parallel and Distributed Systems, vol. 17, no. 11, pp. 1264∼1276, Nov. 2006.

- [19] TOP 500 Supercomputer Sites, Retrieved Feb. 19, 2011, from http://www.top500.org/
- [20] Parallel I/O Benchmarking Consortium, Retrieved Feb. 19, 2011, from http://www.mcs.anl.gov/research/projects/piobenchmark/

