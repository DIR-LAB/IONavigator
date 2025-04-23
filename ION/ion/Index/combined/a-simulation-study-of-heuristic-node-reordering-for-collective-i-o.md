# A Simulation Study of Heuristic Node Reordering for Collective I/O

Kwangho Cha and Sungho Kim Division of Supercomputing, Korea Institute of Science and Technology Information Daejeon, Korea Email: {khocha, sungho}@kisti.re.kr

*Abstract*—As the scale of parallel computing systems grows, the importance of collective I/O also increases because it provides the function of single file based parallel I/O. Collective I/O follows two-phase I/O scheme that consists of a data exchange phase and an I/O phase. The previous studies of collective I/O were usually related with improving the performance of each phase. Especially, Heuristic Node Reordering (HNR) is the technique to improve the data exchange performance where a different number of cores per node are used for a parallel application. In this study, we implement the HNR simulator and analyze the effectiveness of HNR under various cases. As a result, we find out the number of nodes, the maximum number of cores and the shape of I/O data array are the important factors related to improving the HNR performance.

*Keywords*—*Collective I*/*O, I*/*O Aggregator, MPI-IO, Parallel* I/*O, Two-phase I*/O

## I. Introduction

The performance improvement of scientific parallel applications has been achieved via algorithmic optimization or parallelization in general for a long time. As the scale of parallel systems grows and the size of I/O data increases, however, parallel I/O has become an importance issue for improving the performance of parallel applications. Especially, collective I/O is the specialized parallel I/O which supports single-file-based parallel I/O and it also guarantees the independency between the number of processes and the number and structure of files.

Most collective I/O implementations follow two-phase I/O scheme which consists of I/O phase and data exchange phase. For this reason, many previous studies about collective I/O have discussed the topics of data exchange phase and I/O phase. Heuristic Node Reordering (HNR) is a new scheduling method which is proposed to reduce the communication costs in collective I/O in multi-core cluster systems with the different numbers of cores per node[1]. The preliminary experimental results of HNR showed that it is possible to improve the performance of collective I/O by regulating the sequence of nodes in heuristic manner.

In this study, we analyze the effectiveness of HNR and find out the best conditions for adopting HNR, such as the ratio of the number of cores per node to the number of nodes, the shape of array, the number of I/O aggregators per node, and so on. In order to reflect these various conditions, we designed an HNR simulator and performed various kinds of simulations. Based on the simulation results, we concluded that when the number of nodes is harmonized with the number of maximum cores per node, HNR reduces the communication costs in collective I/O remarkably.

The rest of the paper is organized as follows. The main concept of collective I/O and HNR is summarized in Section II. In Section III, we evaluate the effectiveness of HNR by comparing the performance of HNR with that of the optimal solution. Section IV presents the simulation environment and the structure of the HNR simulator. We also discuss the results of simulations in the rest of the section. Finally, the conclusions are presented in Section V.

# II. Related Works

#### *A. Collective I*/O

Today's I/O for computational science applications can be categorized into three types: serial I/O, multi-file based parallel I/O, and single-file based parallel I/O. Because singlefile based parallel I/O doesn't require post processing and provides canonical order of I/O data, its importance increases rapidly these days. Especially, collective I/O is one of the specialized function of single-file based parallel I/O and guarantees the concurrent access to a shared file. The famous parallel programming library, MPI(Message Passing Interface) also provides collective I/O functions, such as MPI File write alland MPI File read all[2].

It has been reported that many scientific applications generate a large number of small data chunks. Because this characteristic can cause serious performance degradation in file I/O, various improvement schemes, such as disk-directed I/O[3] and two-phase I/O[4], have been introduced. MPI-IO(I/O routines of MPI) implementation follows two-phase I/O[4] so as to overcome the problem from the I/O characteristic and improve the collective I/O performance. Many previous studies on improving the performance of collective I/O have been focused on I/O phase related issues such as buffering[5], [6], caching[7], [8], [9], locking[10], [11], file system handling[12] and so on. In addition to these activities, some studies proposed to improve the performance of the data exchange phase by reducing the communication costs of collective I/O[1], [13], [14], [15], [16].

#### *B. Heuristic Node Reordering*

*1) The Concept of Heuristic Node Reordering:* When a High Performance Computing(HPC) system uses nonexclusive scheduling or consists of heterogeneous computational nodes, a different number of CPU cores per node can

![](_page_1_Figure_0.png)

Fig. 1: Example of CPU allocation in a multi-core system using non-exclusive scheduling. In this example, when an MPI job requires eight processes, the job scheduler assigns eight idle CPU cores in four nodes to the task

![](_page_1_Figure_2.png)

Fig. 2: Example of node assignment with different heuristic functions. This figure assumes that a 4×4 array is assigned to 16 processes and eight nodes are selected by the job scheduler to prepare 16 processes. The rounded rectangles represent the nodes as well as the data to be stored or read. Because we also assume each node has single I/O aggregator, there are eight I/O aggregators and eight file domains(FDs). The first process in each node acts as an I/O aggregator and manages its own file domain. For example, the first I/O aggregator is in charge of FD 0. The shaded portions indicate the data that is not moved to I/O aggregators in other nodes

be assigned for parallel jobs. Figure 1 shows the example of job allocation with non-exclusive scheduling. In such systems, if each node uses single I/O aggregator, as the default configuration, each node has the different number of cores and data exchange time in collective I/O will vary according to the sequence of given nodes[1]. Figures 2 and 3 show the example of different communication costs in collective I/O according to the sequence of nodes. Figure 2 depicts the example of different sequence of nodes but they have the same numbers and kinds of nodes. Figure 3, however, demonstrates that there are different communication costs in each node when a collective I/O is issued.

Because the whole data exchange time in collective I/O, Tw(N), is determined by the hot spot node, it is important to reduce the communication costs in the most overloaded node. In other words, when a job scheduler generates a node set N for a parallel job, because each node participates in a data exchange phase concurrently, the whole data exchange time in collective I/O with N is defined by the following equation:

$$T_{w}(N)=c\cdot max\left\{T_{n_{1}},...,T_{n_{i}},...,T_{n_{r}}\right\},\tag{1}$$

where c is an arbitrary coefficient. Tni means the data exchange time in ni, ith node of N, and it can be described as follow:

$$T_{n_{i}}=\alpha\cdot ca_{i}+\beta\cdot ce_{i}+\gamma,\tag{2}$$

where cai is the number of intra-node communications in ni and cei is the number of inter-node communications in ni. The coefficients α and β and the constant γ are determined by the given cluster system1.

The main idea of HNR is find out the good node set N such that minimizes Tw(N). The new node set N- has the same nodes of N but the sequence of nodes are different. It is, however, impossible to get the optimal node set No minimizing communication costs within a polynomial time, because No is the one of the permutations of N and obtaining No requires O(n!) operations. Therefore, we use *heuristic function*s which generate a new node set Nh with the promising sequence of nodes and *heuristic function*s should satisfy the following conditions:

- N: An ordered set of nodes given by a job scheduler.
- Nh: One of the permutations of N. It is generated by a *heuristic function*.
- No: An ordered set of nodes which has the best sequence. It is the optimal node set for data exchange phase and can be obtained by using *exhaustive search*.

<sup>1</sup>In order to get appropriate values of coefficients for a given cluster system, we used an MPI program named cFireworks[1], [17].

![](_page_2_Figure_0.png)

![](_page_2_Figure_1.png)

Fig. 3: Abstract communication model for Fig. 2. The rectangles represent the nodes and the arrows between the nodes indicate the inter-node communication. The arrows in the rectangles are the intra-node communications. The number on the arrows indicates the number of communications. The numbers on(or under) the rectangles represent the number of intra-node communications and that of inter-node communications(intra- : inter-). The thick rectangles indicate the hot spot nodes

## • Np: An ordered set of nodes which has the worst sequence.

If N - Np, then

$$\begin{array}{l}{{T_{w}(N_{o})\leq T_{w}(N_{h})\leq T_{w}(N)}}\\ {{T_{w}(N_{o})\leq T_{w}(N_{h})<T_{w}(N_{p})}}\end{array}$$

In summary, because it is impossible to select No among a large number of permutations of N, we try to use *heuristic function*s for generating Nh which can approximately minimize the maximum communication costs of N. In order to reduce the communication costs, using Nh instead of N is the main concept of HNR[1].

*2) Heuristic Functions for HNR:* In terms of the heuristic functions, we used the same functions in the previous work[1] as in Table I2. Figure 4 shows the example of the number

TABLE I: Heuristic functions in [1]. The example of new node set means the output of the heuristic functions when the given node set is {1,2,3,4,5,6,7,8}.

![](_page_2_Figure_10.png)

Fig. 4: Number of inter-node communications of each node. We use the node set which has 256 processes from 32 nodes

the sequence of nodes

of inter-node communications in each node. The node sets generated by bad heuristic functions such as HF01 and HF02 show that if the large nodes are gathered in the sequence, it causes drastically increased inter-node communications regardless how many numbers of large nodes are in the near neighborhood.

The heuristic functions in the second group generate the smaller number of communications than those in the first group. Considering the number of communications, we concluded that *Modified giant and dwarf* is the most promising heuristic functions for collective I/O.

# III. Evaluation of Heuristic Node Reordering

In this section, we discuss the result of preliminary test. The test was partially done in the previous work[1], but in this work, we focused on comparing the results of HNR and the optimal solutions which were found out using exhaustive search. In order to analyze the performance of the heuristic node reordering, we used a Linux-based cluster system equipped with Lustre file system. The first test used 128 processes with an 8×16 array. Its initial node set was {1,1,1,1,2,2,4,4,8,8,16,16,16,16,16,16} and generated an 8 GB file. The second test assumed that 128 processes managed a 12×12 array and generated a 9 GB file. The initial node set was {1,1,2,2,4,4,6,6,8,14,16,16,16,16,16,16}.

Table II shows the data exchange times of Tests I and II. In the two tests, the heuristic functions HF03, HF04, HF05,

<sup>2</sup>Like the previous work[1], we also use the notation {c0,c1,.....,cn−1} in order to describe the sequence of nodes. The notation indicates that there are n nodes and the first node has c0 CPU cores, the second node has c1 CPU cores, and so on.

![](_page_3_Figure_0.png)

Fig. 5: HNR Simulator

TABLE II: Data exchange times(sec)

| Test I | Test II |  |
| --- | --- | --- |
| Read | Write Read | Write |
| W/O HF | 1.40209 2.45703 1.36764 2.69850 |  |
| HF01: Sort in descending order | 1.43154 2.41445 1.34929 2.65184 |  |
| HF02: Zigzag | 1.39765 2.36277 1.39871 2.64794 |  |
| HF03: Giant and dwarf | 1.19821 1.61131 0.98267 1.82197 |  |
| HF04: Modified giant and dwarf 1.07751 1.49513 1.00746 1.83617 |  |  |
| HF05: Dwarf and giant | 1.06973 1.73331 0.98112 1.86756 |  |
| HF06: Modified dwarf and giant 1.07064 1.62666 1.00831 1.86918 |  |  |
| Optimal Solution | 1.02047 1.42189 0.99565 1.64723 |  |

and HF06 demonstrated better performance than HF01 and HF02. We also checked all the permutation cases of given node set3 and obtained the optimal case which has the minimum communication costs. In case of the first test, the number of possible permutation is 151,351,200 (= 16! 4!·2!·2!·2!·6! ) and only 576 cases generate the same optimal output. The number of permutation of the second test is 1,816,214,400 (= 16! 2!·2!·2!·2!·6! ) and 4048 cases make the same optimal solution. The write performance degradations of using *Modified giant and dwarf* instead of using the optimal solution for Test I and II are 5.15% and 11.47% respectively. Although there is a difference between the performance of the optimal solution and that of *Modified giant and dwarf*, it is still worth to use *Modified giant and dwarf* because it takes a lots of time to find the optimal case by using the brute-force approach.

# IV. Simulation of Heuristic Node Reordering

With the help of preliminary experiments, we could demonstrate that it is acceptable to use HNR instead of finding out the optimal solutions. We, however, also investigated the effectiveness of HNR under various conditions by using simulation approach. In this section, we describe the structure of HNR simulator, the results of simulation and their implications.

#### *A. HNR Simulator*

We designed an HNR simulator as in Fig. 5 so as to verify the usability of HNR under various conditions. The simulator consists of the following routines:

- Random Number Generator: In order to mimic the behavior of a job scheduler of cluster systems, we used a random number generator4. It reads the total
TABLE III: Average number of nodes in Figs. 6, 7 and 8

|  | no. of procs. = 64 |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| maximum cores(A) 4 | 16 | 8 |  | 32 | 64 |
| average no. of nodes(B) 25.825 | 7.860 | 14.506 |  | 4.225 | 2.515 |
| |A − B| 21.825 |  | 6.506 | 8.140 27.775 61.485 |  |  |
| no. of procs. = 144 |  |  |  |  |  |
| maximum cores(A) 4 | 16 | 8 |  | 32 | 64 |
| average no. of nodes(B) 57.957 | 17.189 | 32.266 |  | 9.061 | 4.742 |
| |A − B| 53.957 |  | 24.266 | 1.189 22.939 59.258 |  |  |
| no. of procs. = 256 |  |  |  |  |  |
| maximum cores(A) 4 | 16 | 8 |  | 32 | 64 |
| average no. of nodes(B) 102.832 | 30.428 15.773 | 57.295 |  |  | 8.198 |
| |A − B| 98.832 |  | 49.295 | 14.428 16.227 55.802 |  |  |
| no. of procs. = 512 |  |  |  |  |  |
| maximum cores(A) 4 | 16 | 8 |  | 32 | 64 |
| average no. of nodes(B) 231.233 128.625 |  |  | 68.344 35.236 18.014 |  |  |
| |A − B| 227.233 120.625 | 52.344 |  | 3.236 45.986 |  |  |
| no. of procs. = 1024 |  |  |  |  |  |
| maximum cores(A) 4 | 16 | 8 |  | 32 | 64 |
| average no. of nodes(B) 410.066 228.387 121.120 62.651 31.811 |  |  |  |  |  |
| |A − B| | 406.066 220.387 105.120 30.651 32.189 |  |  |  |  |

number of processes for MPI tasks and the maximum number of cores which can be integrated on a single node and then generates the initial node set.

- Heuristic Functions: These functions regulate the order of nodes in the initial node set and produce the new node sets.
- Prediction Function: The prediction function is based on the equation (2) in Sub-section II-B1 and evaluates the communication performance with the changed node set generated by the heuristic functions5. Because it is necessary to know the I/O access pattern, the routine refers to the parameters for the shape of array and the number of I/O aggregators per node.

### *B. Simulation Results*

Figures 6, 7 and 8 show the results of HNR simulation. The simulations were done with different numbers of I/O aggregators per node and three different shapes of data array6. Each value was normalized by the communication time of the initial node set.

Table III shows the average number of nodes, the maximum number of cores per node and the absolute difference between

<sup>3</sup>The number of all the possible orderings of given node set is the same as the number of permutations with repeated elements.

<sup>4</sup>It is based on Intel Math Kernel Library(MKL)[18].

<sup>5</sup>The previous work[1] has shown that it is possible to predict the communication costs of a given node set by checking the number of communications in the equation (2). We used the same values of the coefficients representing a general Linux-based cluster system in the previous work.

<sup>6</sup>We use two-dimensional arrays that have the different ratio of X-size to Y-size.

![](_page_4_Figure_0.png)

![](_page_4_Figure_1.png)

Fig. 6: Simulation results of HNR. X:Y = 1:1

the average number of nodes and the maximum number of cores per node. According to Figs. 6, 7, 8 and Table III, we can conclude that:

- 1) If there are small number of nodes which have large number of cores or large number of nodes which have small number of core, the effectiveness of HNR is diminished.
- 2) When the number of nodes and the maximum number of cores per node are harmonized, HNR shows meaningful performance. As the absolute difference between the average number of nodes and the maximum number of cores per node in Table III is minimized, HNR shows good performance.
- 3) As the number of I/O aggregators per node is increased, the amount communications also risen and the amount of performance improvement in HNR is decreased.
- 4) In terms of the shape of array, when the array is square or the length of Y is greater than the length of X, HNR shows better performance.

Figure 9 shows the reason why HNR with wide rectangle array in which the length of X is greater than that of Y can't provide differentiated outputs. It draws a distribution of an Y×X arrays onto Z processes, where X·Y = Z and the physical size of the array is μ · ν bytes. Because N nodes are selected to prepare the Z processors, there are N I/O aggregators. In Fig. 9(a), the value of X, Y, Z and N are 6, 2, 12 and 6, respectively. On the other hand, the value of X and Y of Fig. 9(b) are 2 and 6.

Fig. 7: Simulation results of HNR. X:Y = 4:1

The size of Y N in Fig. 9(a) is smaller than that in (b). In addition, the more I/O aggregators manage the I/O requests from a node (or a process). Consequently, in case of λ : 1, I/O request of a process is divided into smaller requests which are served by multiple I/O aggregators. Therefore, even though the sequence of nodes is changed, the changed amount of data in a node which are managed by the I/O aggregator in the same node is relatively small. For example, the changed amount of matched data in n1 is | 2 36 − 1 36 | = 1 36 .

On the other hands, in case of 1 : λ, because few I/O aggregators serve the I/O request of a node (or a process), the amount of changed match rate from node reordering is greater than the case of λ : 1. In the figure, n1's changed amount of matched data is |0 − 1 12 | = 1 12 . Like this, because the amount of changed match rate of a node in 1 : λ is greater than that in λ : 1, the case of 1 : λ is more suitable for HNR. This is the same reason why increasing the number I/O aggregators per node is not good for improving the performance of HNR. Because increasing the number of I/O aggregators per node also results in decreasing the size of Y N and increasing the number of I/O aggregators for I/O requests of nodes.

In addition to the basic simulation, we studied the sensitivity of HNR to the number of cores in nodes. Although the first simulation assumed the number of cores per node (=α) is uniformly in the range of [1, c], where c means the maximum number of cores per node, we changed the range of minimum cores per node in the second simulation. This condition reflects the case where jobs do not have small number of cores per node. Figures 10 and 11 show the

![](_page_5_Figure_0.png)

simulation results of HNR with different range of cores per node when the number of I/O aggregators per node is one. Although the performance improvement decreases slightly as the minimum number of cores per node increases, HNR still shows improved performance in some cases, such as using a number of processes or a narrow array (X < Y).

## V. Conclusions

When an HPC system uses non-exclusive scheduling, the I/O aggregators that perform important roles in collective I/O have different workload amounts and nodes also have different communication costs. In the proposed heuristic node reordering, the order of the nodes is changed by a job scheduler before launching the MPI task so as to reduce skewed communication loads on the nodes. In this study, we re-evaluated the performance of HNR and showed that using HNR is a meaningful alternative instead of finding out the optimal solution.

We also designed an HNR simulator and with the help of the simulator we could expect the performance of HNR. The simulation results implied that when the number of nodes is similar to the number of maximum cores per node, HNR will show good performance improvement. Based on the results, we also believe that the performance of HNR depends on the shape of array which should be stored and the number of I/O aggregators. At this time because we only have used basic block distribution, it is necessary to consider the effect of other data distribution such as cyclic distribution in the near future.

![](_page_5_Figure_5.png)

Fig. 9: Examples of X:Y = λ : 1 and X:Y = 1 : λ

## References

- [1] Kwangho Cha, and Seungryoul Maeng, "Reducing Communication Costs in Collective I/O in Multi-core Cluster Systems with Nonexclusive Scheduling," in The Journal of Supercomputing, vol. 61, no. 3, pp. 966∼996, Sep. 2012.
- [2] William Gropp, Ewing Lusk, and Rajeev Thakur, "Using MPI-2: Advanced Features of the Message Passing Interface," The MIT Press, Nov. 1999.
- [3] David Kotz, "Disk-directed I/O for MIMD multiprocessors," in ACM Transactions on Computer Systems, vol. 15, no. 1, pp.41∼74, Feb. 1997.
- [4] Rajeev Thakur, and Alok Choudhary, "An Extended Two-Phase Method for Accessing Sections of Out-of-Core Arrays," in Scientific Programming, vol. 5, no. 4, pp. 301∼317, 1996.
- [5] Bill Nitzberg, and Virginia Lo, "Collective Buffering: Improving Parallel I/O Performance," in Proc. of the IEEE International Symposium on High Performance Distributed Computing, pp. 148∼157, Aug. 1997.
- [6] Xiaosong Ma, Marianne Winslett, Jonghyun Lee, and Shengke Yu, "Improving MPI-IO Output Performance with Active Buffering Plus Threads," in Proc. of the International Parallel and Distributed Processing Symposium, Apr. 2003.
- [7] Wei-Keng Liao, Kenin Coloma, Alok Choudhary, and Lee Ward, "Cooperative Client-Side File Caching for MPI Applications," in International Journal of High Performance Computing Applications, vol. 21, no. 2, pp. 144∼154, May 2007.
- [8] Wei-Keng Liao, Kenin Coloma, Alok Choudhary, Lee Ward, Eric Russell, and Sonja Tideman, "Collective Caching: Application-aware Client-side File Caching," in Proc. of the 14th IEEE International

![](_page_6_Figure_0.png)

![](_page_6_Figure_1.png)

Fig. 10: Simulation results of HNR. α ∈ [ c 4 , c]

Symposium on High Performance Distributed Computing, pp. 81∼90, Jul. 2005.

- [9] Wei-keng Liao, Avery Ching, Kenin Coloma, Arifa Nisar, Alok Choudhary, Jacqueline Chen, Ramanan Sankaran, and Scott Klasky, "Using MPI File Caching to Improve Parallel Write Performance for Large-Scale Scientific Applications," in Proc. of the 2007 ACM/IEEE conference on Supercomputing, Article no. 8, Nov. 2007.
- [10] Wei-keng Liao, Kenin Coloma, Alok Choudhary, Lee Ward, Eric Russell, and Neil Pundit, "Scalable Design and Implementations for MPI Parallel Overlapping I/O," in IEEE Transactions on Parallel and Distributed Systems, vol. 17, no. 11, pp. 1264∼1276, Nov. 2006.
- [11] Wei-keng Liao, "Design and Evaluation of MPI File Domain Partitioning Methods under Extent-Based File Locking Protocol," in IEEE Transactions on Parallel and Distributed Systems, vol. 22, no. 2, pp. 260∼272, Feb. 2011.
- [12] Phillip M. Dickens, and Jeremy Logan, "A high performance implementation of MPI-IO for a Lustre file system environment," in Concurrency and Computation: Practice and Experience, vol. 22, no. 11, pp. 1433∼1449, Aug. 2010.
- [13] Kwangho Cha, "An Efficient I/O Aggregator Assignment Scheme for Multi-core Cluster Systems," in IEICE Transactions on Information and Systems, vol. E96-D, no. 2, pp. 259∼269, Feb. 2013.
- [14] Kwangho Cha, and Seungryoul Maeng, "An Efficient I/O Aggregator Assignment Scheme for Collective I/O Considering Processor Affinity," in Proc. of the International Conference on Parallel Processing Workshops 2011(SRMPDS 2011), pp. 380 ∼ 388, Sep. 2011, Taipei, Taiwan.
- [15] Kwangho Cha, Taeyoung Hong, and Jeongwoo Hong, "The Subgroup Method for Collective I/O," The 5th International Conference on Parallel and Distributed Computing, Applications and Technologies (PDCAT 2004), LNCS 3320, pp. 301∼304, Dec. 2004.
- [16] Weikuan Yu, and Jeffrey Vetter, "ParColl: Partitioned Collective I/O on the Cray XT," in Proc. of the 37th International Conference on Parallel Processing, pp. 562∼569, Sep. 2008.
- [17] Kwangho Cha, "cFireworks: a Tool for Measuring the Communication

Fig. 11: Simulation results of HNR. α ∈ [ c 2 , c]

Costs in Collective I/O," International Journal of Advanced Computer Science and Applications, vol. 5, no. 8, Aug. 2014.

- [18] Intel Math Kernel Library (Intel MKL) https://software.intel.com/enus/articles/intel-math-kernel-library-documentation Accessed 27 Mar. 2015.
