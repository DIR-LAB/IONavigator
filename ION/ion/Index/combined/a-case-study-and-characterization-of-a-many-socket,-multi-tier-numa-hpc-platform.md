# A Case Study and Characterization of a Many-socket, Multi-tier NUMA HPC Platform

Connor Imes *USC Information Sciences Institute* Arlington, VA, USA cimes@isi.edu

Steven Hofmeyr *Lawrence Berkeley National Laboratory* Berkeley, CA, USA shofmeyr@lbl.gov

Dong In D. Kang *USC Information Sciences Institute* Arlington, VA, USA dkang@isi.edu

John Paul Walters *USC Information Sciences Institute* Arlington, VA, USA jwalters@isi.edu

*Abstract*—As the number of processor cores and sockets on HPC compute nodes increase and systems expose more hierarchical non-uniform memory access (NUMA) architectures, efficiently scaling applications within even a single shared memory system is becoming more challenging. It is now common for HPC compute nodes to have two or more sockets and dozens of cores, but future generation systems may contain an order of magnitude more of each. We conduct experiments on a state-of-the-art Intel Xeon Platinum system with 12 processor sockets, totaling 288 cores (576 hardware threads), arranged in a multi-tier NUMA hierarchy. Platforms of this scale and memory hierarchy are uncommon today, providing us a unique opportunity to empirically evaluate—rather than model or simulate—an architecture potentially representative of future HPC compute nodes. We quantify the platform's multi-tier NUMA patterns, then evaluate its suitability for HPC workloads using a modern HPC metagenome assembler application as a case study, and other HPC benchmarks with a variety of parallelization techniques to characterize the system's performance, scalability, I/O patterns, and performance/power behavior. Our results demonstrate nearperfect scaling for embarrassingly parallel and weak scaling workloads, but challenges for random memory access workloads. For the latter, we find poor scaling performance with the default scheduling approaches—e.g., which do not pin threads suggesting that userspace or kernel schedulers may require changes to better manage the multi-tier NUMA hierarchies of very large shared memory platforms.

*Index Terms*—high performance computing, performance analysis

## I. INTRODUCTION

Modern HPC compute nodes now contain dozens of processor cores, often with multiple CPU sockets. For example, both Summit at ORNL and Sierra at LLNL have two CPU sockets per node, each with 22 processor cores [40]. These trends are expected to continue, e.g., for Aurora at ANL, expected in 2021 [15]. There is also a growing demand today for very large shared memory systems in HPC for particular types of workloads like genome assembly [6], cosmology [34], and AI [38]. Some HPC clusters are even provisioned for such workloads, like Genepool at NERSC [11].

Processor manufacturers are also designing for larger-scale shared memory systems. For example, Intel recently released Cooper Lake processors that target 4- and 8-socket server-class systems, with up to 28 cores (56 threads) per socket [37]. There are increasing numbers and variety of systems with several NUMA layers, supported architecturally by multiple kinds of interconnects. While there has been considerable research in the last decade on efficiently using NUMA systems, NUMA effects are becoming more pronounced as systems continue to scale, resulting in greater research interest in just the last several years [4, 6, 10, 13, 33, 36]. It is critical that we understand the behavior of very large, hierarchical shared memory systems both to support larger shared memory workloads today and so that we can better design applications for future HPC platforms with similar characteristics.

In this paper, we evaluate a massively parallel HPE Superdome Flex (SDF) system to characterize its usefulness as a HPC platform [14]. This state-of-the-art platform is composed of 12 high-end Intel Xeon Platinum processors arranged in a multi-tier NUMA architecture, with 9 TiB of shared DRAM. As a case study, we evaluate a modern HPC genomics application on the platform and compare with results from the Cori supercomputer at NERSC. To better understand the fundamental properties of the platform, we conduct a variety of additional experiments to measure CPU and memory performance, scaling, and variation; weak scaling; multi-level parallelism; I/O; and performance/energy tradeoffs.

Specifically, we make the following contributions:

- Describe the architecture of a state-of-the-art 12-socket, multi-tier NUMA system.
- Conduct an empirical case study with a HPC metagenome assembly application and compare with executions on NERSC Cori.
- Characterize the highly-NUMA platform with HPC benchmarks supporting different parallelization strategies (e.g., OpenMP, MPI, MPI+OpenMP) by varying processor scale, HyperThreading, and process pinning.
- Evaluate additional system properties like parallel I/O and performance/energy tradeoffs.
- Discuss lessons learned from our experiments and suggest areas for future work.

![](_page_1_Figure_0.png)

Fig. 1: Node-to-node NUMA behaviors (darker color is better).

#### II. BACKGROUND AND MOTIVATION

To demonstrate potential challenges in utilizing a large multi-tier NUMA platform, Figure 1 both quantifies and visualizes the memory latency and bandwidth patterns measured on the 12-socket evaluation platform using Intel's Memory Latency Checker [41]. On this platform, NUMA Nodes map one-to-one with processor sockets, and every four NUMA Nodes form a NUMA Group. Data points on the diagonal (upper left to lower right) measure local memory access within a NUMA Node. As should be expected, these measurements produce the best latency and bandwidth – 81 ns and 107 GB/s, respectively.

In Figure 1a, the 4 × 4 darker-colored regions indicate the lower latencies for accessing data within a NUMA Group, relative to accessing data outside the NUMA Group. Latency is about 81 ns within a NUMA Node (i.e., local memory access), around 132 ns to access memory in two neighboring Nodes, and between 210–215 ns to access memory in the remaining Node in the Group. When accessing memory outside of the NUMA Group, latencies are around 360 ns. In Figure 1b, a similar pattern is seen for bandwidth, with more extreme loss within a NUMA Group, making it very difficult to distinguish the NUMA Group boundary by color. NUMA Nodes achieve about 107 GB/s locally, then bandwidth drops dramatically to around 16.7–16.9 GB/s for the other Nodes in the Group. When accessing memory outside of the NUMA Group, bandwidth is typically 12.6–12.7 GB/s. In short:

- Memory latency is not uniform even between all NUMA Nodes within a Group and increases by 60–70% with each additional hop outside of a NUMA Node.
- Memory bandwidth decreases by an order of magnitude when non-local memory access is required.

These patterns indicate that applications that cannot keep the majority of data near to the compute threads requiring it could be severely impacted by suboptimal thread and data management, even on a shared memory system. But these are exactly the kinds of applications that do not distribute well and thus are often limited to running on large shared memory systems. Therefore, efficiently managing the NUMA hierarchy on such platforms is particularly important for memory latency- and bandwidth-sensitive applications whose threads regularly request non-local memory, i.e., outside of a NUMA Node, and especially outside of a NUMA Group. Applications that are subject to these access patterns must overcome these challenges if they are to scale even within a single shared memory system.

An example of such applications are metagenome assemblers, which commonly run on very large shared memory systems. Metagenomes are collections of genomes, from potentially thousands of microbial species, which are mixed together when an environmental sample is sequenced, e.g., from a soil sample, the human gut, or around an oil spill. Assembling these genomes supports far better understanding of these microbial communities, with benefits in areas such as human health, agriculture, biofuels, and environmental cleanups. However, these samples can be huge—terabases of sequenced reads—and require far more memory (multiple terabytes) to assemble than is available in typical shared memory server-class systems. The very reasons that these applications are often limited to shared memory platforms also limit their scalability within those systems. For example, we tried evaluating a popular parallel metagenome assembler on the 12-socket platform but found that it did not scale beyond even a single socket [29].

MetaHipMer supports very large scale metagenome assemblies and is capable of scaling on large distributed memory systems efficiently [18, 21]. A dominant computation pattern in MetaHipMer is distributed hash table updates and accesses, making memory latency critical, while other application stages are bandwidth-constrained. Additionally, these computational patterns *do not port well to accelerators like GPUs*, necessitating efficient random memory access and communication using general purpose CPUs. Running MetaHipMer on a cluster is only feasible if the interconnect is very fast, i.e., at least InfiniBand—high speed Ethernet is not sufficient. Most commercially accessible clusters do not have a sufficiently high speed interconnect, motivating the use of large shared memory systems instead. Thus, MetaHipMer's distributed design makes it an excellent candidate for a case study on our large multi-tier NUMA platform.

## III. EXPERIMENTAL DESIGN

Our evaluation platform, an HPE Superdome Flex (SDF), contains 12 Intel Xeon Platinum 8168 processors and 9 TiB of DRAM. The system is composed of three chassis, each with four processor sockets connected by Intel Ultra Path Interconnects (UPI) in a ring fashion. A third UPI from each socket is connected to an HPE ASIC which interconnects with other chassis to enable global shared memory and cache coherence. The four sockets in each chassis form a NUMA Group, and each socket is a separate NUMA Node. Each socket has 24 physical cores, each with a HyperThread, for a total of 288 physical cores or 576 compute threads. Processors have a 2.7 GHz base frequency, a maximum TurboBoost of 3.7 GHz, and a 205 Watt thermal design power (TDP). The system runs Red Hat Enterprise Linux 7.8.

Our case study uses MetaHipMer, a *de novo* metagenome assembler application representing a class of applications that are often run on large shared memory systems [18, 21]. MetaHipMer is developed as a successor to HipMer, a high performance, distributed memory and scalable metagenome assembler [17]. A primary motivation behind its development is a new software architecture using UPC++ which allows better opportunities for overlapping communication and computation, and simplifies program implementation, thus improving application scalability, efficiency, and maintainability. To date, MetaHipMer has primarily been developed and tested on a large quad socket shared memory platform and in a distributed setting on NERSC Cori. We evaluate MetaHipMer performance on the SDF and compare with results on Cori Haswell and KNL compute nodes.

Additionally, we evaluate a set of common HPC benchmark applications to quantify different aspects of the system's performance and scalability. From the NAS Parallel Benchmarks, we use EP (Embarrassingly Parallel) to quantify compute behavior, IS (Integer Sort) for its random memory access patterns, and BT and SP both for supporting multi-level parallelism using MPI+OpenMP and since they are pseudoapplications and thus more complex/realistic than kernel applications [2]. STREAM measures sustained memory bandwidth and parallelizes embarrassingly well [31]. Finally, AMG [20] and XSBench [39] are weak scaling applications and IOR measures I/O performance [28].

We compile applications on the SDF with GCC 9.1.0. MPI applications use OpenMPI 4.0.2 and MetaHipMer uses UPC++ 2020.3.0, both also compiled with the aforementioned GCC. On Cori, GCC 7.5.0 is the base compiler.

We evaluate application performance and scalability by varying the socket counts, HyperThreads, and use of thread pinning (binding software threads to CPUs). Execution times are reported by the applications. Some experiments also measure performance counters using the PCM tool to provide insight into application behavior at the architectural level [32]. We limit PCM to producing results at socket granularity to minimize the overhead, which we find to be negligible.

## IV. EVALUATION

This section presents the evaluation of the 12-socket, multitier NUMA Superdome Flex (SDF) platform, beginning with a case study of the MetaHipMer metagenome application in Section IV-A. Sections IV-B–IV-E characterize fundamental properties of the platform including compute and memory performance, scaling, and variation. Sections IV-F and IV-G evaluate multi-level parallel and weak scaling applications, respectively. Sections IV-H and IV-I evaluate file system I/O behavior and performance/power tradeoffs. We conclude the evaluation with a discussion of lessons learned and future work in Section IV-J.

In various figures throughout the evaluation, we demonstrate application run times and the relative scaling, using executions on a single socket as a baseline for application speedup at different socket counts. When HyperThreads are used—the

0 2 4 6 8 10 12 0 400 800 1200 1600 Sockets Runtime (sec) HT-Pin Phys-Pin HT-nopin Phys-nopin 0 2 4 6 8 10 12 0 2 4 6 8 10 12 Sockets Speedup

Fig. 2: MetaHipMer runtime (left) and relative scalability (right).

*HT-pin* and *HT-nopin* configurations—48 threads per socket are allocated to the application to match the number of physical cores and hardware threads available. When HyperThreads are not used—the *Phys-pin* and *Phys-nopin* configurations— 24 threads per socket are allocated to the application to match the number of physical cores only. When pinning is used, threads are bound to physical cores first, then to HyperThreads if they are also in use.

## *A. Case Study: MetaHipMer*

Figure 2 shows the runtime and the relative scalability for the MetaHipMer metagenome assembly application. A crucial observation is that when thread pinning is not used, performance degrades significantly as the application scales across the NUMA Group boundaries between 4–5 and 8– 9 sockets. In these cases, the software scheduler appears to be making poor placement decisions when migrating threads. This is likely due to threads being migrated outside of their original NUMA Node and Group, resulting in increased memory latencies, which MetaHipMer is very sensitive to. The Figure 1 heat map in Section II and further evaluation of memory-bound benchmarks in Sections IV-C and IV-D below support this hypothesis.

At 12 sockets, a 7.5× speedup is achieved with HyperThreads and a 8.0× speedup is achieved with physical cores only. The best performance is consistently achieved using HyperThreads with thread pinning, despite its overall speedup being slightly lower—the physical cores only baseline performance is simply worse. We conclude that the application scales reasonably well when thread pinning is used, especially considering the application's random memory access patterns and the platform's multi-tier NUMA architecture (e.g., compare with Figure 8 below in Section IV-D).

Figure 3 compares these results against executions on NERSC Cori Haswell compute nodes, with thread pinning enabled on both platforms. As before, the SDF results are captured at socket granularity, i.e., 24-core increments; the Cori Haswell results are captured at node granularity, i.e., 32-core increments. The per-core comparison is remarkably similar between these two very different platforms as we scale, especially when only using the physical cores. Although the SDF contains high-end Xeon Platinum processors, MetaHipMer

![](_page_3_Figure_0.png)

Fig. 3: MetaHipMer runtime comparison with Cori Haswell.

TABLE I: MetaHipMer runtime comparison with Cori Haswell at 288 cores.

| Platform | HyperThreads | Runtime (sec) | Coeff. of Variation |
| --- | --- | --- | --- |
| SDF | yes | 144 | 1.93% |
|  | no | 172 | 1.46% |
| Cori | yes | 167 | 1.08% |
| Haswell | no | 170 | 1.85% |

exhibits random memory access patterns, mostly negating the benefit of the powerful processors (see Section IV-I for performance/power behavior). Many phases in the MetaHipMer execution are strongly impacted by memory latencies, the rest are bandwidth-bound. For example, we find that when thread pinning is not used and performance degrades dramatically between 4 and 5 sockets, the most latency-sensitive phases of MetaHipMer suffer the largest performance degradation.

The SDF also makes better use of HyperThreads than Cori Haswell. Using HyperThreads on the SDF consistently achieves the best performance—144 seconds compared to 172 seconds at maximum scale. Cori benefits from HyperThreads at lower node counts, but these benefits diminish as we scale out further. Table I quantifies the runtime and performance variation at 288 cores, i.e., all 12 sockets on the SDF and 9 Cori Haswell nodes. We compute performance variation at 288 cores using 5 executions on each platform and find that the results are comparable. We expected that the distributed Cori Haswell executions would exhibit higher variability than on the shared memory SDF. However, Cori has a state-of-theart low latency, high bandwidth interconnect that is superior to what most commercial clusters can provide. These results suggest that MetaHipMer might successfully distribute across multiple very large shared memory systems networked with a high-speed interconnect.

We also evaluated MetaHipMer on Cori Xeon Phi KNL nodes, primarily to see how many nodes are needed to match the SDF performance. Only physical cores are tested on Cori KNL, where each KNL node has one socket with 68 cores. We find that 20 Cori KNL nodes (1,360 cores) beat the SDF physical core-only performance, but 25 Cori KNL nodes (1,700 cores) are needed to match the SDF HyperThread performance. We also observe that performance is much more variable on the KNL nodes. For example, some 25 node executions perform worse than some 20-node executions.

![](_page_3_Figure_7.png)

Fig. 4: EP runtime (left) and relative scalability (right).

The random access memory patterns in MetaHipMer limit scalability, and using the weaker KNL cores appears to be problematic.

In summary, MetaHipMer scales reasonably well, particularly for an application that is memory-bound, both in latency and bandwidth, and exhibits random memory access patterns (compare with Section IV-D below). However, proper thread pinning is required when scaling beyond NUMA Group boundaries, otherwise there is severe performance degradation. Despite the SDF system having higher-class processors than Cori Haswell, per-core performance is comparable when HyperThreads are not used. MetaHipMer is also better tested and optimized on Cori, and the shared memory platform still outperforms Cori Haswell core-for-core when HyperThreads are used. The scalability results on both the SDF and Cori Haswell also suggest that multiple very large shared memory systems might be successfully networked to support similar workloads.

#### *B. Parallel Compute Scalability*

Figure 4 shows the runtime and the relative scalability for the EP (Embarrassingly Parallel, class D) compute-bound application. It is immediately clear that only one configuration, *Phys-pin*, scales as it should. We expected that at least *HT-pin* would also scale near-perfectly, even though it has a different (faster) baseline performance. It is difficult to distinguish in the figure because lines overlap, but at low socket counts both HyperThread configurations behave nearly identically to each other and both physical core configurations behave nearly identically to each other. Pinning has no quantifiable performance benefit at socket counts 1–4, which is reasonable since all data is still close to the compute threads—within the same NUMA Group at least—even if they are migrated, and threads should not be sharing data.

As we allocate additional sockets, we expect the configurations that use pinning to scale the best since EP still has some memory dependencies that are best kept local to the computation. All configurations scale near-perfectly up to 4 sockets, which comprise a NUMA Group, then there is some scaling degradation starting at 5 sockets, when the NUMA Group boundary is crossed. Pinning without HyperThreads begins to outperform pinning with HyperThreads, which suddenly starts losing performance at 7 sockets.

![](_page_4_Figure_0.png)

Fig. 5: FREQ performance counter behavior at socket granularity for two EP executions using HyperThreads – with (top) and without (bottom) thread pinning.

To investigate, we examine resource utilization at the architectural level by monitoring hardware performance counters with PCM [32]. To capture a reasonable number of data points, we switch to the E class benchmark size. We visualize this behavior using the FREQ performance counter, which we find is a good socket utilization indicator for the OpenMP implementation of EP. FREQ is the ratio of actual CPU frequency to the CPU's base frequency (i.e., the maximum non-TurboBoost frequency).

Figure 5 presents the FREQ performance counter behavior at socket granularity for two EP executions using HyperThreads with all 12 sockets allocated. The execution in the top chart is when thread pinning is used, the execution in the bottom chart is when thread pinning is not used. When thread pinning is used (upper plot), FREQ drops occur after about 110–120 seconds on some sockets well before others, indicating that those sockets have finished processing their assigned workload. When thread pinning is not used (lower plot), similar behavior occurs at the same time, but all sockets remain at least partially utilized for the remainder of the execution, which is much shorter than when pinning is used. This is likely a result of threads being moved between sockets (between NUMA Nodes or even NUMA Groups). While this thread movement improves (decreases) the total runtime, the EP workload is intended to be distributed evenly, so there appears to be a different problem that thread relocation partially alleviates but does not completely mask.1

We also observe differences in the maximum FREQ values achieved by each socket. Sockets with higher FREQ values appear to also require the most time to complete processing. In contrast, at smaller socket allocations (not shown), FREQ values between allocated sockets are much more consistent both in maximum value (< 1.2) and in duration (sockets complete at similar times). Performance degradation becomes

![](_page_4_Figure_6.png)

Fig. 6: STREAM runtime (left) and relative scalability (right).

more noticeable as socket allocations increase, e.g., in the 5–8 socket range (2 NUMA Groups), and we begin to see much more inconsistency at 9–12 sockets (3 NUMA Groups), like in Figure 5.

Finally, we test whether EP's MPI implementation exhibits the same scaling problem with HyperThreads, though we omit a figure due to space limitations. With pinning enabled, EP scales near-perfectly up to 12 sockets both with HyperThreads and with physical cores only. Additionally, when running on physical cores, the MPI and OpenMP runtimes are extremely similar at all socket counts, indicating that the algorithm itself is scalable and the MPI and OpenMP versions *should* behave similarly. We conclude that the EP scaling problems observed are limited to the OpenMP implementation. Further analysis is needed to track down the cause of the problem, but it appears to be a software issue, e.g., with the application implementation, with the OpenMP library, or with Linux kernel. Despite this problem, we are still able to demonstrate the platform's capacity for excellent compute scalability.

## *C. Parallel Memory Scalability*

Figure 6 shows the average iteration runtime and the relative scalability for the STREAM memory-bound application. Proper thread and data placement is extremely important with STREAM since memory locality is necessary to optimize memory latency and bandwidth, as quantified and visualized in Figure 1 in Section II. Using thread pinning, both with and without HyperThreads, scales near-perfectly at all socket counts. Additionally, performance is consistent regardless of HyperThreads when pinning is used, which makes sense for a memory-bound application that cannot benefit from additional compute resources which do not also include additional memory bandwidth.

Not pinning threads results in performance degradations that vary greatly beyond 4 sockets (the first NUMA Group boundary). In these configurations, threads may be moved across NUMA Nodes and NUMA Groups. However, such poor thread management at higher socket counts suggests that the software schedulers are failing to account for NUMA impacts when they opt to move threads across NUMA boundaries. This behavior clearly demonstrates the need for better hierarchyaware thread and data placement scheduling in hierarchical NUMA systems. Thread and data pinning is only one option

<sup>1</sup>For example, sockets in the first NUMA Group seem to finish first, so one possibility is that OpenMP is not allocating data on the correct nodes.

![](_page_5_Figure_0.png)

Fig. 7: FREQ performance counter behavior at socket granularity for two STREAM executions using HyperThreads – with (top) and without (bottom) thread pinning.

that may not necessarily be optimal for more complex applications and dataflows.

We examine performance counters for STREAM as we did with EP. To capture sufficient data points, we lengthen the application runtime by increasing the number of kernel executions from 10 to 100. Figure 7 presents the FREQ performance counter behavior at socket granularity for two STREAM executions using HyperThreads with all 12 sockets allocated. When thread pinning is used (upper plot), we observe what we expect from an application with near-perfect scalability – the system sockets are fully utilized for nearly the entire duration of the application execution. The few seconds at the end where FREQ is low is just the application summarizing its runtime results. When thread pinning is not used (lower plot), the behavior is very different – FREQ does not remain at its maximum value and the runtime is considerably longer. We also observe (but not show due to space limitations) that READ performance is consistently about 5× worse, WRITE performance is about 2−3× worse, and there is a considerable amount of UPI traffic (whereas there is very nearly none when thread pinning is used—only at the end when the results are being summarized). We observe similar results as those in Figure 7 when HyperThreads are not used. These results support the conclusion that threads are indeed being moved between sockets by the software schedulers.

#### *D. Random Memory Access*

Figure 8 shows the average iteration runtime and the relative scalability for the IS (Integer Sort, class D) application. In contrast to STREAM, with its regular memory access patterns, IS exhibits random memory access patterns. We now see significant performance losses when crossing the NUMA Group boundaries between 4–5 and 8–9 sockets for all configurations, not just without thread pinning like in STREAM. After the initial performance degradation when crossing a NUMA Group boundary, adding additional sockets (e.g., sockets 6, 7, and 8) slowly improves performance until the next boundary

![](_page_5_Figure_6.png)

Fig. 8: IS runtime (left) and relative scalability (right).

TABLE II: Performance variation of EP and STREAM.

| Benchmark | HyperThreads | Coeff. of Variation | Range (Norm.) |
| --- | --- | --- | --- |
| EP | yes | 1.54% | 6.01% |
|  | no | 1.47% | 4.57% |
| STREAM | yes | 0.240% | 0.689% |
|  | no | 0.163% | 0.601% |

is crossed and performance suffers again. This behavior is similar to that observed with MetaHipMer (Figure 2 in Section IV-A). However, MetaHipMer achieved considerably better scaling, supporting our earlier conclusion that it scales well for an application with random memory access patterns.

These results clearly demonstrate the performance impact on some applications resulting from the multi-level NUMA hierarchy. A simplistic recommendation is to never use a partial NUMA Group, or even more than a single NUMA Group in this case. However, many applications exhibit random access behavior to varying degrees and/or only during certain execution phases. Improved awareness of the memory hierarchy may still support improving performance by using the available resources.

#### *E. Performance Variation*

We evaluate performance variability between sockets using EP (a compute-bound benchmark) and STREAM (a memorybound benchmark), with OpenMP thread pinning enabled. Although variability exists at core granularity, cores in a socket share the L3 cache and memory controller which can make it difficult to distinguish between variability caused by the CPUs and variability caused by competition for these shared resources. Cores in a socket compose a NUMA Node, and since a socket "owns" the memory hierarchy up to the local DRAM, sockets are effectively self-contained entities in the memory hierarchy when only local memory is used. We execute a separate instance of each application on each of the 12 sockets in parallel (effectively a weak scaling test, as well). The problems identified earlier with EP scaling are a non-issue here since those problems do not occur at low socket counts, and each EP instance in this test is limited to a single socket.

Table II summarizes the results when testing with and without HyperThreads, averaged over three executions each. EP has coefficients of variation that are an order of magnitude higher than STREAM, which supports attributing most of the variation to processor compute behavior. We also present the

![](_page_6_Figure_0.png)

Fig. 9: BT (top) and SP (bottom) runtime (left) and relative scalability (right).

normalized performance range ((tmax − tmin)/tmin), which more clearly describes how much faster or slower work on different sockets can be. This is important for application developers to quantify since uniformly parallel operations are limited by the slowest resource.

In addition to these results, we observed that each socket's performance is consistent between executions. For each socket, we evaluate the coefficient of variation across each application's three executions and summarize by averaging these values across the 12 sockets. We find the 12 sockets' average coefficient of variation is 0.22% with HyperThreads and 0.19% without HyperThreads for EP, and 0.095% and 0.080%, respectively, for STREAM.

Together, these results indicate the presence of hardware manufacturing variation—or a similar systemic property which applications can measure and adapt to [1, 8, 24, 42]. For example, applications might re-balance workloads to assign some work from slower sockets to faster sockets, ideally eliminating timing imbalances in parallel workloads and speeding up the application. Alternatively, faster sockets can be "slowed down" to save power/energy without sacrificing performance over the baseline (determined by the slowest socket) – see Section IV-I below for more on performance/power tradeoffs.

#### *F. Multi-level Parallelism*

The previous experimental evaluations demonstrated the compute and memory scalability of the platform using flat parallelization techniques. We now examine applications with multi-level parallelism using MPI+OpenMP. Such applications hierarchically partition their work, using message passing between processes (e.g., across distributed systems) and threading within each process (e.g., within a shared a memory system). We therefore expect that these workloads should scale very well on the SDF given its multi-tier NUMA architecture. Figure 9 shows the runtime and the relative scalability of the BT and SP NAS pseudo-applications for both multi-level and flat parallelism approaches.

For MPI+OpenMP multi-level parallelism, we map MPI ranks by socket and pin OpenMP threads to cores and hardware threads within sockets. Using HyperThreads improves performance in both applications, but with a small scalability loss at higher socket counts relative to only using physical cores. BT achieves very good scalability at 12 sockets (i.e., 12 MPI processes) – 11.2× and 11.7× speedups with and without HyperThreads, respectively. SP also scales well – 10.8× and 11.1× speedups with and without HyperThreads, respectively.

We also test both applications with OpenMP-only and MPIonly executions using physical cores only with thread pinning. BT with OpenMP-only is faster at one socket than with MPI+OpenMP. However, OpenMP-only achieves only a 6× speedup at 12 sockets, with MPI+OpenMP overtaking the OpenMP-only runtime at 4 sockets. SP with OpenMP-only is slower than MPI+OpenMP at one socket and only achieves 6.7× speedup at 12 sockets. The MPI-only executions are slower for both applications in all cases. However, the MPIonly implementations do not always use all the allocated MPI ranks when we scale at socket granularity (e.g., 1 socket uses 16 ranks, but 10 sockets uses 225 ranks), hence the superlinear speedup values for MPI-Phys-Pin. Still, MPI scalability suggests that the message passing structure may eventually be beneficial at larger scales, so MPI-only may still be worth exploring on larger shared memory systems.

We find that these pseudo-applications scale well using multi-level parallelism (MPI+OpenMP), indicating that hierarchical parallelism provides benefits over flat OpenMP parallelism on the multi-tier NUMA architecture. The next natural step is to add distributed systems back into the hierarchy, which might benefit from an additional parallelism layer so that a hierarchical parallelism can still be used within a large shared memory system.

## *G. Weak Scaling*

We evaluate the platform's capacity to support weak scaling workloads using the AMG and XSBench applications, which have poor strong scaling but are designed to scale weakly. When weak scaling, both applications use multi-level parallelism—MPI+OpenMP—where adding additional MPI ranks adds additional work. AMG decomposes a 3-D grid across MPI ranks; we scale the workload by setting Py = n when using n ranks. In XSBench, no decomposition is performed across ranks – each rank performs the same work as others. We map MPI ranks by socket and pin OpenMP threads to cores and hardware threads within sockets.

Figure 10 demonstrates both the strong and weak scalability of these applications. As clearly seen from the charts on the left, strong scaling is very poor. For example, strong scaling XSBench with OpenMP provides performance gains up to 3 sockets, then performance begins to degrade. In contrast, the charts on the right demonstrate near-perfect weak scaling, where a perfectly flat curve would indicate that no additional time is needed to process the increasing workload sizes as

![](_page_7_Figure_0.png)

Fig. 10: AMG (top) and XSBench (bottom) strong scaling (left) and weak scaling (right) runtimes.

![](_page_7_Figure_2.png)

Fig. 11: IOR write performance to Lustre file system.

sockets are added. AMG does not benefit from HyperThreads, and loses about 6% of its baseline performance when scaling beyond the first socket, with additional slow degradation as more sockets are added. XSBench clearly benefits from HyperThreads, but unlike AMG, exhibits perfect weak scaling as additional sockets are added.

The platform clearly handles weak scaling applications well, as should be expected—indeed it would be indicative of more fundamental problems if there were issues. These results primarily help verify that the system behaves as it should, using non-trivial applications rather than kernel benchmarks like EP and STREAM.

## *H. I/O*

A strong motivation for using large shared memory systems is the lower communication and synchronization overhead between parallel computations. However, application performance is still impacted by the system's I/O capacity. HPC applications read large inputs and write large outputs from/to persistent storage, and sometimes perform large amounts of I/O during execution, e.g., between application phases or to perform checkpoint/restore operations for fault tolerance. These I/O operations should run efficiently so that the application can continue making forward progress. Thus, it is still important to understand I/O performance.

We evaluate the SDF's write performance on a Lustre file system connected by InfiniBand. Figure 11 demonstrates write performance achieved with IOR, using physical cores only. When MPI ranks are mapped by core, a socket's cores are fully allocated before a new socket is used. When MPI ranks are mapped by socket, sockets are allocated in a round-robin manner, and only after all 12 sockets are allocated a rank do ranks start to be allocated to additional cores on each socket.

First, we test with MPI processes writing to a shared file. Mapping by core (*shar-by-core*) outperforms mapping by socket (*shar-by-sock*). Mapping by core peaks at the 12-rank configuration (using half of the cores on one socket). Using 24 ranks (all cores on one socket) doesn't improve performance, and in fact degrades it a bit. Performance then begins to fall further as additional sockets are utilized. Mapping by socket performs poorly, where the 12-rank configuration (12 sockets, each with one core) is the best, and adding additional ranks does not improve performance—in fact, there is some performance loss. Application profiling shows increasing application dormant state as scaling increases, leading us to suspect that lock contention is limiting performance, especially across sockets.

We then test with each MPI process writing to independent files. Mapping by core (*ind-by-core*) again outperforms mapping by socket (*ind-by-sock*). Mapping by core peaks at 96 MPI ranks, which is equivalent to using all the physical cores on 4 sockets (a complete NUMA Group). We expect that this is the maximum performance achievable with the file system, and that adding additional ranks is over-saturating the file system. Mapping by socket generally achieves performance gains as additional MPI ranks are allocated, but does not achieve the same throughput as mapping by core. When testing with direct I/O, mapping by socket and by core achieve almost identical performance, leading us to suspect that there is still some synchronization overhead despite using independent files [25].

It is clear that scheduling I/O on this platform is not trivial and requires careful consideration. It is disappointing that writing to shared files performs so poorly when the file partitioning should support throughput more similar to independent files when using a parallel file system like Lustre. The lower performance both when using shared files and when mapping I/O tasks by socket suggests that shared state and/or lock contention limit I/O scalability.

#### *I. Performance/Power Tradeoffs*

Power consumption is a growing concern in the HPC domain, so it is also critical that we understand performance/power tradeoffs in large shared memory systems which may be representative of future HPC compute nodes. We return again to our case study application, MetaHipMer, and to the EP and STREAM benchmarks to evaluate these tradeoffs on the SDF. To explore this tradeoff space, we execute the applications under a range of RAPL power caps [9,

![](_page_8_Figure_0.png)

Fig. 12: EP, STREAM, and MetaHipMer power cap tradeoffs with runtime (left) and energy consumption (right).

22]. Specifically, we adjust the short term package power constraints in 20 Watt increments, between 60 W and 220 W, and normalize runtime and energy consumption to those at the default power cap of 246 W for each application. Applications run on physical cores only with thread pinning. We use PCM to collect actual energy consumption of both the power capped processors and the uncapped DRAM.

Figure 12 presents the normalized runtime and energy consumption of these applications for different power caps. The processors' TDP is 205 W, meaning they cannot sustain power consumption above that level for very long, which is why results are relatively flat at the highest power caps. Application performance generally begins to degrade as the power cap is reduced, which is normal behavior for most applications since the processors are forced to run at lower DVFS frequencies. Memory-bound applications, like STREAM and MetaHipMer, are impacted less by the changes at higher power caps because they are not able fully utilize the available processor power. For example, STREAM only uses a maximum of about 110 W of processor power, even when the power cap is considerably higher, so its performance is not impacted until the power cap approaches this level. In contrast, computebound applications like EP, which utilize nearly all available processor power, begin losing performance quickly as the power cap is reduced.

It has been shown that maximum resource utilization (e.g., using maximum DVFS frequencies) is not the most energyefficient resource scheduling approach [26]. The energy consumption results in Figure 12 reflect this fact. The most efficient power caps, i.e., the ones with the lowest energy consumption for a complete application execution, are 180 W for EP, 100 W for STREAM, and 110 W for MetaHipMer. The energy savings for each application over their baselines are 6%, 13%, and 16%, respectively. Also recall that these measurements include both the power capped processor and uncapped DRAM energy consumption, so further gains might be found by also managing the DRAM power caps.

The SDF exhibits a performance and power tradeoff space that can be navigated by power/energy-aware software. Some potential reasons to do so are to optimize energy consumption, reduce energy subject to performance constraints, or maximize performance while respecting power caps, e.g., in a hardware over-provisioned environment. Furthermore, the best decision for a given circumstance may depend on the applications running on the system.

## *J. Discussion and Future Work*

These empirical results demonstrate both the benefits and challenges in using a very large shared memory system with a multi-tier NUMA hierarchy. Our case study with MetaHipMer, a metagenome assembly application, demonstrates comparable—and sometimes better—performance and scalability compared to using the Cori supercomputer at NERSC, on which the application is originally developed and optimized. A series of additional experiments quantify and demonstrate performance and scalability of different types of applications on our evaluation platform.

We were initially surprised that MetaHipMer scaled similarly on the SDF as on Cori Haswell. The performance is similar core-for-core, despite the SDF having superior processors and and order of magnitude lower memory latencies between NUMA Groups than Cori has between nodes (memory latencies across NUMA Groups on the SDF are around 360 ns and latencies between nodes on Cori are 5–8 us [12]). However, the UPC++ framework that MetaHipMer uses supports efficient asynchronous communication and computation, thus masking these overheads well. Additional investigation may still be helpful, e.g., to evaluate if cache coherence is impacting performance for an application that is designed to work in a distributed environment. We verified that corefor-core performance is not the same by running the MPI implementation of EP class E on both platforms and found that 11 nodes (352 cores) are required on Cori Haswell to match the SDF's performance at 12 sockets (288 cores).

We are also surprised at the low performance variation measured on Cori with MetaHipMer. We anticipated that variation would be considerably higher on Cori relative to the SDF. This may also be a result of the application's memoryboundedness, where memory access latencies dominate the effects of hardware process variation and competition for a shared interconnect, which UPC++ may also be helping to mask.

When we first evaluated MetaHipMer on the SDF, there had not yet been a compelling reason for the application to implement thread pinning. However, when we began scaling outside of a single NUMA Group (beyond 4 sockets), we experienced the extreme performance degradations seen for the non-pinning results in Figure 2 (Section IV-A). Pinning immediately resulted in a performance boost on both the SDF and on Cori. This same type of behavior is seen with STREAM and IS benchmarks, but had not been identified before we began evaluating MetaHipMer. Further investigation is needed to determine why the system software (likely the Linux kernel or OpenMP library implementation) is moving threads with such disastrous results on performance (see Figure 6 in Section IV-C).

Additionally, HyperThreads had previously not been considered useful for MetaHipMer. The results on Cori support this mindset when scaling beyond a handful of nodes, but the benefits of HyperThreading on the SDF are obvious even as we scale to all 12 sockets on the system. Common wisdom among HPC developers and users holds that HyperThreads are not useful and often harmful, so we encourage reexamining these assumptions when using large shared memory systems. We found that for most applications and benchmarks, using HyperThreads provides performance benefits, or at worst provides no benefits without being harmful. The exception was with EP, which still requires further investigation to identify why it exhibits the problems we visualize with the FREQ performance counter (see Figure 5 in Section IV-B).

The MetaHipMer developers also feel it might be worthwhile to consider a more hierarchical implementation, using threads within shared memory in a NUMA domain, e.g., with one process per NUMA Node or NUMA Group. Of course, potential performance gains need to be balanced with the complexity introduced by the requisite code restructuring. Additionally, grouping processes on distributed large shared memory nodes and aggregating network traffic between systems may be beneficial at certain scales.

Utilizing multiple very large shared memory systems in a distributed environment will introduce additional challenges hinted at in this evaluation. For example, further study is needed to evaluate efficient networking, I/O, and persistent file systems to support fewer but larger collaborating shared memory systems. New software frameworks, programming, and runtime techniques may be needed to support application developers in managing this growing complexity.

#### V. RELATED WORK

Several works have examined very large shared memory systems, including the HPE Superdome Flex (SDF) architecture, with varying processor type and socket/core counts. Bang et al. revisit earlier predictions of 1000-core architectures and evaluate a 28-socket (784-core, 1568-thread) SDF for DBMS workloads, which the SDF architecture and its predecessors were originally designed for [3]. Baskaran et al. evaluate tensor decomposition methods on both a cluster and a 16-socket (288-core) SDF [5]. Most similar to this paper, Becker et al. recently analyze bioinformatics applications on a 16-socket (144-core, 288-thread) SDF with with 6 TB of memory [6]. These works demonstrate the demand for, and utility of, large shared memory platforms for HPC workloads. While they focus on specific applications and domains, we use a genomics application only as a case study, extending our evaluation to characterize the large NUMA platform more generally for HPC workloads.

There is a growing body of recent work on managing NUMA effects on shared memory platforms. Barrera et al. use task dependency graphs to optimize OpenMP applications on two large multi-socket systems—a 6-socket (96-core) SGI Altix UltraViolet 100a and a 16-socket (288-core) Atos Bull bullion S16 [36]. More recent work proposes optimizing NUMA thread/data placement and the hardware prefetcher configuration using a machine learning model [4]. Gawade and Kersten show that significant remote memory access still occurs in database systems running on NUMA systems as the number of threads increase, even when data affinity is kept local to sockets [16]. Drebes et al. use deferred allocation and enhanced work-pushing for NUMA-aware task and data placement on a 192-core system with 24 NUMA nodes [13]. Denoyelle et al. choose thread and data placement strategies in NUMA systems using a black-box approach on Intel Haswell, Broadwell, and Skylake systems [10]. Popov et al. search across a range of parameters to optimize performance on NUMA systems [33].

Performance heterogeneity due to process variation is also an increasing concern as systems scale. Inadomi et al. study performance and power heterogeneity due to manufacturing variability in distributed, power-constrained environments and adjust power allocations to improve application performance [24]. Acun et al. study variation, particularly under TurboBoost, on several HPC platforms [1]. Chasapis et al. adjust power and concurrency levels to address manufacturing variability and improve HPC application performance [8].

Power consumption is also a growing concern in the HPC domain, and recent years have seen in increase related research. DOE has set a 20 MW power goal for exascale systems [27], which still requires improvements in energy efficiency to achieve [7]. For example, Imes et al. demonstrate the benefits of maximizing energy efficiency on a quad-socket shared memory system, including for genomics applications [23]. Adagio saves energy in HPC applications while minimizing performance loss [35]. Similarly, Gholkar et al. adjust uncore frequency scaling to save energy [19]. CoPPer optimizes energy consumption subject to runtime performance constraints [22]. Conductor distributes power to nodes and cores to improve performance in power-constrained environments [30].

#### VI. CONCLUSION

As HPC systems evolve to contain fewer but more powerful nodes, scalability within even a single node is becoming more challenging, particularly due to increasing NUMA patterns. We conduct an empirical evaluation of a state-of-the-art shared memory platform with a multi-tier NUMA hierarchy and 12 high-end Intel Xeon Platinum processors—a total of 288 cores, or 576 threads—and 9 TiB of shared DRAM. As a case study, we evaluate a state-of-the-art HPC metagenome assembler, representing a class of applications commonly run on large shared memory systems due to difficulties in distributing their computations and in utilizing accelerators like GPUs. We also characterize the platform with a collection of common HPC benchmarks and pseudo-applications to demonstrate its performance and scalability, and additionally study I/O behavior and performance/power tradeoffs. Our results demonstrate the platform's suitability for HPC workloads while revealing challenges and potential areas for future work.

#### REFERENCES

- [1] B. Acun, P. Miller, and L. V. Kale, "Variation among processors under turbo boost in hpc systems," in ICS, 2016.
- [2] D. H. Bailey, E. Barszcz, J. T. Barton, D. S. Browning, R. L. Carter, L. Dagum, R. A. Fatoohi, P. O. Frederickson, T. A. Lasinski, R. S. Schreiber, H. D. Simon, V. Venkatakrishnan, and S. K. Weeratunga, "The nas parallel benchmarks–summary and preliminary results," in SC, 1991.
- [3] T. Bang, N. May, I. Petrov, and C. Binnig, "The tale of 1000 cores: An evaluation of concurrency control on real(ly) large multi-socket hardware," in *DaMoN*, 2020.
- [4] I. S. Barrera, D. Black-Schaffer, M. Casas, M. Moreto, A. Stupnikova, ´ and M. Popov, "Modeling and optimizing numa effects and prefetching with machine learning," in ICS, 2020.
- [5] M. Baskaran, T. Henretty, and J. Ezick, "Fast and scalable distributed tensor decompositions," in HPEC, 2019.
- [6] M. Becker, U. Worlikar, S. Agrawal, H. Schultze, T. Ulas, S. Singhal, and J. L. Schultze, "Scaling genomics data processing with memorydriven computing to accelerate computational biology," in *High Performance Computing*, 2020.
- [7] M. Berry, T. E. Potok, P. Balaprakash, H. Hoffmann, R. Vatsavai, Prabhat, and R. Pino. (2015). "Machine learning and understanding for intelligent extreme scale scientific computing and discovery," [Online]. Available: http : / / science . energy. gov / ∼ / media / ascr / pdf / program documents/docs/Machine Learning DOE Workshop Report.pdf (visited on 07/15/2020).
- [8] D. Chasapis, M. Casas, M. Moreto, M. Schulz, E. Ayguad ´ e, J. Labarta, ´ and M. Valero, "Runtime-guided mitigation of manufacturing variability in power-constrained multi-socket numa nodes," in ICS, 2016.
- [9] H. David, E. Gorbatov, U. R. Hanebutte, R. Khanna, and C. Le, "Rapl: Memory power estimation and capping," in *ISLPED*, 2010.
- [10] N. Denoyelle, B. Goglin, E. Jeannot, and T. Ropars, "Data and thread placement in numa architectures: A statistical learning approach," in *ICPP*, 2019.
- [11] N. Documentation. (2020). "Cori for jgi," [Online]. Available: https: / / docs . nersc . gov / science - partners / jgi / cori - genepool/ (visited on 07/15/2020).
- [12] D. Doerfler, B. Austin, B. Cook, J. Deslippe, K. Kandalla, and P. Mendygral, "Evaluating the networking characteristics of the cray xc-40 intel knights landing-based cori supercomputer at nersc," *Concurrency and Computation: Practice and Experience*, vol. 30, no. 1, 2018, e4297 cpe.4297.
- [13] A. Drebes, A. Pop, K. Heydemann, A. Cohen, and N. Drach, "Scalable task parallelism for numa: A uniform abstraction for coordinated scheduling and memory management," in PACT, 2016.
- [14] H. P. Enterprise. (2020). "HPE superdome flex servers," [Online]. Available: https://www.hpe.com/us/en/servers/superdome.html (visited on 07/15/2020).
- [15] A. L. C. Facility. (2020). "Aurora argonne leadership computing facility," [Online]. Available: https://alcf.anl.gov/aurora (visited on 07/15/2020).
- [16] M. Gawade and M. Kersten, "Numa obliviousness through memory mapping," in *DaMoN*, 2015.
- [17] E. Georganas, A. Buluc¸, J. Chapman, S. Hofmeyr, C. Aluru, R. Egan, L. Oliker, D. Rokhsar, and K. Yelick, "Hipmer: An extreme-scale de novo genome assembler," in SC, 2015.
- [18] E. Georganas, R. Egan, S. Hofmeyr, E. Goltsman, B. Arndt, A. Tritt, A. Buluc¸, L. Oliker, and K. Yelick, "Extreme scale de novo metagenome assembly," in SC, IEEE, 2018.
- [19] N. Gholkar, F. Mueller, and B. Rountree, "Uncore power scavenger: A runtime for uncore power conservation on hpc systems," in SC, 2019.
- [20] V. E. Henson and U. M. Yang, "BoomerAMG: A parallel algebraic multigrid solver and preconditioner," *Appl. Numer. Math.*, vol. 41, no. 1, Apr. 2002.
- [21] S. Hofmeyr, R. Egan, E. Georganas, A. C. Copeland, R. Riley, A. Clum, E. Eloe-Fadrosh, S. Roux, E. Goltsman, A. Buluc¸, *et al.*, "Terabase-scale metagenome coassembly with metahipmer," *Scientific reports*, vol. 10, no. 1, 2020.
- [22] C. Imes, H. Zhang, K. Zhao, and H. Hoffmann, "CoPPer: Soft realtime application performance using hardware power capping," in *ICAC*, 2019.
- [23] C. Imes, S. Hofmeyr, and H. Hoffmann, "Energy-efficient application resource scheduling using machine learning classifiers," in *ICPP*, 2018.
- [24] Y. Inadomi, T. Patki, K. Inoue, M. Aoyagi, B. Rountree, M. Schulz, D. Lowenthal, Y. Wada, K. Fukazawa, M. Ueda, M. Kondo, and I. Miyoshi, "Analyzing and mitigating the impact of manufacturing variability in power-constrained supercomputing," in SC, 2015.

- [25] D. I. D. Kang, J. P. Walters, and S. P. Crago, "Scalable parallel file write from a large numa system," in *HPEC*, 2020.
- [26] D. H. K. Kim, C. Imes, and H. Hoffmann, "Racing and pacing to idle: Theoretical and empirical analysis of energy optimization heuristics," in *CPSNA*, 2015.
- [27] P. Kogge, S. Borkar, D. Campbell, W. Carlson, W. Dally, M. Denneau, P. Franzon, W. Harrod, J. Hiller, S. Keckler, D. Klein, and R. Lucas, "Exascale computing study: Technology challenges in achieving exascale systems," *DARPA IPTO, Techinal Representative*, vol. 15, Jan. 2008.
- [28] L. L. N. Laboratory. (2019). "HPC IO benchmark repository," [Online]. Available: https://github.com/hpc/ior (visited on 08/31/2020).
- [29] D. Li, C.-M. Liu, R. Luo, K. Sadakane, and T.-W. Lam, "MEGAHIT: an ultra-fast single-node solution for large and complex metagenomics assembly via succinct de Bruijn graph," *Bioinformatics*, vol. 31, no. 10, Jan. 2015.
- [30] A. Marathe, P. E. Bailey, D. K. Lowenthal, B. Rountree, M. Schulz, and B. R. de Supinski, "A run-time system for power-constrained hpc applications," in ISC, 2015.
- [31] J. D. McCalpin, "Memory bandwidth and machine balance in current high performance computers," *IEEE TCCA Newsletter*, Dec. 1995.
- [32] opcm. (2020). "Processor counter monitor (pcm)," [Online]. Available: https://github.com/opcm/pcm (visited on 07/15/2020).
- [33] M. Popov, A. Jimborean, and D. Black-Schaffer, "Efficient thread/page/parallelism autotuning for numa systems," in ICS, 2019.
- [34] P. Release. (Nov. 2017). "Hpe partners with stephen hawking's cosmos research group and the cambridge faculty of mathematics," [Online]. Available: https://www.hpe.com/us/en/newsroom/press- release/2017/ 11/hpe-partners-with-stephen-hawkings-cosmos-research-group-andthe-cambridge-faculty-of-mathematics.html (visited on 07/15/2020).
- [35] B. Rountree, D. K. Lowenthal, B. R. de Supinski, M. Schulz, V. W. Freeh, and T. Bletsch, "Adagio: Making dvs practical for complex hpc applications," in ICS, 2009.
- [36] I. Sanchez Barrera, M. Moret ´ o, E. Ayguad ´ e, J. Labarta, M. Valero, and ´ M. Casas, "Reducing data movement on large shared memory systems by exploiting computation dependencies," in ICS, 2018.
- [37] T. Trader. (Jun. 2020). "Intel debuts cooper lake xeons for 4- and 8-socket platforms," [Online]. Available: https://www.hpcwire.com/ solution content/intel/intel- debuts- cooper-lake- xeons- for- 4- and- 8 socket-platforms/ (visited on 07/15/2020).
- [38] ——, (Jun. 2020). "Neocortex will be first-of-its-kind 800,000-core ai supercomputer," [Online]. Available: https:// www. hpcwire . com/ 2020/ 06/ 09/ neocortex - will - be - first - of - its - kind - 800000 - core - ai supercomputer/ (visited on 07/15/2020).
- [39] J. R. Tramm, A. R. Siegel, T. Islam, and M. Schulz, "XSBench the development and verification of a performance abstraction for monte carlo reactor analysis," in *PHYSOR*, 2014.
- [40] S. S. Vazhkudai, B. R. de Supinski, A. S. Bland, A. Geist, J. Sexton, J. Kahle, C. J. Zimmer, S. Atchley, S. Oral, D. E. Maxwell, V. G. V. Larrea, A. Bertsch, R. Goldstone, W. Joubert, C. Chambreau, D. Appelhans, R. Blackmore, B. Casses, G. Chochia, G. Davison, M. A. Ezell, T. Gooding, E. Gonsiorowski, L. Grinberg, B. Hanson, B. Hartner, I. Karlin, M. L. Leininger, D. Leverman, C. Marroquin, A. Moody, M. Ohmacht, R. Pankajakshan, F. Pizzano, J. H. Rogers, B. Rosenburg, D. Schmidt, M. Shankar, F. Wang, P. Watson, B. Walkup, L. D. Weems, and J. Yin, "The design, deployment, and evaluation of the coral preexascale systems," in SC, 2018.
- [41] V. Viswanathan, K. Kumar, T. Willhalm, P. Lu, B. Filipiak, and S. Sakthivelu. (Jun. 2020). "Intel memory latency checker v3.9," [Online]. Available: https:// software.intel. com/ content/www/ us/ en/ develop/ articles/intelr-memory-latency-checker.html (visited on 07/22/2020).
- [42] N. Zompakis, M. Noltsis, L. Ndreu, Z. Hadjilambrou, P. Englezakis, P. Nikolaou, A. Portero, S. Libutti, G. Massari, F. Sassi, A. Bacchini, C. Nicopoulos, Y. Sazeides, R. Vavrik, M. Golasowski, J. Sevcik, V. Vondrak, F. Catthoor, W. Fornaciari, and D. Soudris, "Harpa: Tackling physically induced performance variability," in *DATE*, 2017.

