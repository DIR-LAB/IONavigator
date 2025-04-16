# Ensemble-Based System Benchmarking for HPC

1 st Anna Fuchs *Universitat Hamburg* ¨ Hamburg, Germany anna.fuchs@uni-hamburg.de

2 rd Jannek Squar *Universitat Hamburg* ¨ Hamburg, Germany jannek.squar@uni-hamburg.de

3 nd Michael Kuhn *Otto von Guericke University of Magdeburg* Magdeburg, Germany michael.kuhn@ovgu.de

405 

2024 23rd Intern

*Abstract*—In HPC supercomputers, the CPU, memory, network and storage play a critical role in application performance. Established benchmarks measure the theoretical peak performance of these components, but storage benchmarks often focus solely on I/O and lack realism. To address this, we present **numio**, a benchmark that simulates and evaluates overlapping compute, communication and I/O phases.

Furthermore, we present a novel ensemble-driven system benchmarking strategy. This approach involves running multiple benchmarks in parallel to analyse their interactions and assess the system's ability to handle the workload. Using a real-world example, we demonstrate how this approach reveals performance issues in complex HPC systems that remain hidden when using traditional methods using isolated benchmarks on empty systems.

*Index Terms*—System benchmarking, HPC, parallel I/O, network congestion, system, compression, asynchronous workloads

#### I. MOTIVATION

Input/output (I/O) plays a crucial role in scientific applications due to the large amount of data generated. Examples include climate simulations and computational fluid dynamics. Interfacing with storage devices can lead to performance issues because latencies are significantly higher than those within the processor. Efficient storage systems are therefore important for optimal application performance. Highperformance computing (HPC) vendors are moving towards exascale systems to tackle larger problems, but efficient data movement remains a challenge. Existing storage systems are often evaluated using synthetic I/O benchmarks that do not accurately represent real scientific applications and neglect the interplay between computation, communication and I/O. To address these complexities, we propose a new benchmark called numio that accurately simulates numerical computation, communication and I/O phases in real-world applications and remains configurable like a synthetic benchmark. We also introduce a benchmarking strategy for HPC systems based on semi-synthetic benchmarks of different categories. This ensemble approach allows us to capture the interactions and dependencies between jobs, providing a more comprehensive understanding of system performance.

## II. HPC NATURE AND BENCHMARKS

HPC systems are evolving into increasingly complex and heterogeneous architectures. In a traditional HPC system, many nodes communicate over high-speed networks that can reach speeds of tens of gigabytes per second per node. The dominant file system architecture in the HPC I/O domain is the client-server model with clients being computing nodes. Client nodes have powerful CPUs dedicated to processing calculations for individual applications. Servers, on the other hand, act as shared storage nodes, often with larger memory capacities and faster network connections. Both the client and server sides run distributed parallel file systems such as Lustre. While client nodes are dedicated to specific jobs, the network and file system are shared resources with overlapping loads.

System characteristics have a significant impact on performance. CPU attributes, such as frequency and cache size, mainly influence computation speed. The size of main memory sets boundaries on problem sizes and influences buffering capabilities. Memory-bound applications are typically constrained by the speed of main memory, impacting the rate at which data can be fetched and processed. This primarily affects computation, as other tasks within an application often struggle to match such latencies. Network speed and latency is critical for communication between nodes, and storage speed and IOPS (I/O operation per second) limits disk I/O.

## *A. Asynchronicity*

The various tasks within an application are illustrated in Figure 1, also providing illustrative examples of their respective patterns. While communication often requires lower network throughput (represented by shorter bars), it places significant demands on latency (shown by numerous small requests in succession). The computational aspect (referred to as "calculation" here to avoid confusion with compression) may be either CPU-bound or memory-bound, as indicated in the diagram. Additionally, compression and encryption, which are specialized forms of computation for data transformation, may also occur. These two types of data transformations have contrasting effects on I/O network transfer and disk transmission (each depicted by negative and positive lines), as they can either increase or decrease data volume.

The efficiency of systems relies on the overlapping of processes, maximizing the utilization of all resources simultaneously. However, this poses an issue when various tasks compete for the same resources, potentially hindering one another. Asynchrony in operations primarily pertains to internal processes within applications or jobs, where resource competition can occur either locally within nodes or across nodes. Another layer involves inter-job interferences, directly affecting only shared resources but capable of indirectly in-

![](_page_1_Figure_0.png)

Fig. 1: Example tasks within an application and their resource demands with schematic patterns and positive and negative impacts.

![](_page_1_Figure_2.png)

Fig. 2: Simplified asynchronous layers (I/O disk, I/O network, compression, calculatio, communication) in a pipeline and their interaction and mutual interference across nodes.

fluencing exclusively allocated resources, thereby potentially altering the behavior of the entire application. Some examples are given in Figure 2.

Cases A and B each represent distinct applications executed independently on a system. Job A exclusively focuses on I/O tasks, with data compression being its sole CPU-intensive component. In contrast, Job B lacks any I/O operations and consists solely of tightly consecutive calculations and asynchronous communication with other nodes (not depicted in the image). These illustrations represent the execution of these applications under ideal conditions. Moving on to Case C, it illustrates the scenario where A and B are part of the same application running on a single node. Here, one can observe how tasks, competing for the same resources as previously described, can obstruct one another, leading to delays. In Case D, we see another job or application executed across three (or more) nodes, with only one node engaged in I/O operations. This scenario highlights how delays within nodes caused by I/O operations affect other nodes, which would not have been affected otherwise. Given the sensitivity of inter-node communication to latency, even minor delays can have significant consequences. Moreover, as more nodes are involved, the aggregated effects worsen, known as idle waves. These idle waves can subsequently affect communication and I/O phases, and ultimately the overall execution of the application [1; 2; 3].

In scenario E, we illustrate how two jobs competing for I/O resources can have retroactive effects on the computational workload of the first job. This occurs because the ideal overlap between I/O and computation can no longer be achieved. If the compute-intensive job in this scenario also engages with additional communication partners, like in case D, it will similarly exert detrimental effects on the other nodes' performance.

While there are undoubtedly more metrics, and their mutual influence is considerably more complex due to additional caching layers and tons of system optimizations per layer, this serves as an initial step in understanding the significance of these interactions.

#### *B. Benchmarks*

Despite understanding the complexity of systems and their crucial, performance-critical interactions, benchmarks fail to capture any of this depth. Nowadays, it is common to run separate benchmarks or applications for each performance metric on an empty system to evaluate its performance. The de facto standard synthetic I/O benchmarks are IOR and mdtest. These widely used benchmarks are employed in compute centers when procuring new storage systems and in almost every I/O-related scientific study. Their primary purpose is stress testing large-scale storage systems and verifying their peak performance.

However, establishing a direct correlation between resources and application behavior is challenging due to complex interactions. For example, doubling CPU power does not simply cut a benchmark's runtime in half; it can also shift bottlenecks. As described before, the interactions between computation, memory accesses, and asynchronous I/O phases are nonlinear and cannot be reliably predicted over extended periods of time [4; 5].

Some studies focus on compensating for insufficient I/O performance by using compute or memory resources [6; 7; 8; 9]. Unfortunately, synthetic I/O benchmarks typically overlook this interaction. Therefore, it is critical to evaluate both the performance of individual components and their collective behavior across applications.

![](_page_2_Figure_0.png)

Fig. 3: Simulated system benchmarking upper limits accuracy.

Figure 3 shows the approximation of real production load by means of different benchmarking strategies. We believe that by using a small set of representative benchmarks similar to our own, and incorporating additional benchmarks for other groups such as machine learning (ML), post-processing, etc., we can establish an improved and generic method for evaluating system performance. This approach eliminates the need to build and set up countless specific applications for the evaluation process. Additionally, it enables the implementation of a relatively practical strategy, facilitating improved assessment of system requirements.

Consequently, these benchmarks serve various operational domains within HPC. They assist operators in conducting more effective cost-benefit analyses and in making informed decisions regarding the suitability of potential systems for their specific needs. For manufacturers, these benchmarks are designed to be clear and easily understandable. Furthermore, they support middleware and system developers in testing new features, such as compression or encryption (not limited to), if they were to be introduced. Additionally, application developers can leverage these benchmarks to evaluate the potential impact of adjusting various parameters within their applications, determining whether the development effort for a particular system is justified.

#### *C. Middleware Use Cases and Features*

System benchmarking or middleware analysis are examples of use cases that benefit from interaction analysis. For example, client-side data reduction in parallel file systems aims to improve network and disk I/O performance, but at the cost of increased computation. When benchmarking I/O alone, using the most intensive compression algorithm can negatively impact overall runtime or even cause memory issues, aspects that synthetic I/O benchmarks fail to address.

In the same manner, functionalities like asynchronous file synchronization [10] impact both I/O and computation. This requires adjustments to benchmarks by introducing artificial computation phases to examine the impact of such features.

Network congestion can be a significant challenge due to the massive amount of data generated and processed by HPC systems. As scientific applications and simulations become more data-intensive, the network can become a limiting factor, adversely affecting overall system performance. Congestion can lead to higher latency, reduced throughput, and prolonged job completion times. We are conducting extensive research on this specific use case in Section IV-C.

## *D. Related Work*

This section covers the most common I/O-related benchmarks in the HPC field as well as numerical applications and frameworks with best representative computation loads.

HPL [11] and HPCG [12] are popular benchmarks for measuring FLOPS, but they do not account for I/O performance.

elbencho [13; 14] claims to be a user-friendly benchmark for testing GPU storage access, while h5bench [4] is designed for real HDF5 applications with support for asynchronous modes. However, these benchmarks neglect communication and memory usage overlap. StressBench [15] offers a similar approach like numio by implementing kernels for computation, communication and I/O to represent realword HPC applications. numio allows to use more backends and the user can configure the composition of computation, communication and I/O during runtime.

Several works [16; 17; 18; 19] prove that I/O access patterns are critical to file system performance, but the impact of application compute phases on I/O access is neglected. Other studies [20; 21; 22] work on balancing the I/O load for better overall performance. Their effect is difficult to measure with peak-oriented benchmarks, though.

#### III. BENCHMARK DESIGN

We have designed a new benchmark intended to be capable of representing multi-stage and incrementally different tasks, each to varying depths. Recognizing the vast diversity of applications and acknowledging that it is impossible to anticipate every aspect, we ensure that the benchmark is easy to understand, modular, and extensible. This is to prevent it from becoming just another incomplete and poorly usable benchmark in the collection.

The design of numio is straightforward and modular, making it easy to implement changes, such as introducing new computation patterns or I/O backends, with minimal effort.

*Data Structures and Mathematics:* Partial Differential Equations (PDEs) play an important role in many scientific simulations and engineering applications involving numerical computing. A common implementation involves iteration and operates on two different matrices representing the square grid. Complex stencils such as 2D nine-point boxes or 3D stars with seven or more points are possible [23]. Perturbation functions regulate the computational intensity and CPU load, demonstrated by simple and complex functions in our prototype. The problem size is defined by the number of rows and columns.

*Parallelization:* The parallelization of numio encompasses computation, communication, and I/O. The matrix is divided into nearly uniform blocks, and during each iteration, the adjacent upper and lower rows are exchanged between neighboring processes. In our benchmarks, we are able to switch communication modes, where each block is calculated first and either simultaneously or afterwards the halo lines are communicated to neighboring processes. The computation phases of the processes are therefore synchronized after each iteration. I/O is performed on the submatrix by each process in different modes and supported backends.

*Overlapping Modes:* The key feature of our benchmark is the overlapping of different phases, which is illustrated in Figure 4 using the example of the MPI-IO backend (while we will skip the description of HDF5, NetCDf, ADIOS and further WIP-backends for space reasons).

*sync+imm* (Figure 4a): Blocking write calls per process with immediate file synchronization. In this scenario, the compute and I/O phases are executed in a serialized manner because the compute phase does not start until the disk synchronization has been completed.

*sync* (Figure 4b): The I/O function operates in a blocking mode, while disk synchronization occurs after the subsequent compute phase, just before the next write operation. However, the ability of the client node to buffer the request allows computation to continue while the data is being transferred over the network and/or synchronized on disk.

*async* (Figure 4c): This mode maximizes asynchronicity between the computation and I/O phases. It uses a nonblocking write that is completed by the end of the computation.

![](_page_3_Figure_4.png)

(c) Non-blocking write with delayed file synchronization.

Fig. 4: Different overlapping and synchronization I/O modes of the benchmark numio.

*Metrics and Settings* We offer performance metrics, including runtime, data throughput, empirical FLOPS, and the number of communicated (MPI) and transferred data (I/O) for the specific phases when possible. However, in asynchronous and overlapping modes, isolating them becomes a challenge. To address this, we present these metrics per application run, obtained by dividing the total number of bytes written by the total runtime for data throughput.

We can specify a read or write rate, represented as a frequency over the number of iterations. To illustrate unbalanced patterns, we can also apply a weight to the base pattern. For example, -w freq=5,pattern=10:0:1 would write every 5 iterations, but increase writes tenfold in the first third of all write phases, skip the middle third of I/O, and write one matrix regularly in the last third.

*Ensembles:* Designing appropriate ensembles for specific HPC systems is a challenging task that is difficult to fully

![](_page_3_Figure_10.png)

Fig. 5: Comparison of IOR and numio benchmark ensembles for up to 9 concurrent jobs.

automate. However, we provide scripts with basic architectures for several scenarios: *empty* (single run on an empty system), *balanced* (default with wide range of settings), *peak:metric* (stressing I/O, CPU, etc.), and *custom* (user settings). Regarding *peak*, we have the flexibility to designate individual tasks or applications as x-bound, all the while considering their other task components. This approach ensures that when testing a system optimization for a particular bottleneck, we take into account what potential impact on other metrics its shifting might have.

#### IV. EVALUATION

Due to space constraints, we will skip the trivia to show the different behaviors of different overlapping modes in our benchmarks. We are first examining several ensemble scenarios to demonstrate the impact of ensemble runs on benchmark performance using IOR and numio to show how their usage could lead to different assumptions in a hardware procurement process. Next, we will illustrate how the benchmark could be used to explore the potential benefits of various compression strategies for an application. Following that, we will demonstrate how our benchmark could uncover issues related to network congestion.

#### *A. Synthetic*

We designed three types of benchmark ensembles to compare performance degradation under additional system load. They were run on a locked-down system where we could ensure that the network and file system were not being used by other users. We used up to 10 compute clients (Intel Xeon CPU X5650, 12 GiB memory) and 5 storage servers (Intel Xeon CPU E31275, 16 GiB memory) with 1 Gb/s Ethernet interconnect. All tests show the runtime results of the reference job on an empty and busy system, normalized to the runtime on the empty system. We performed 1 to 9 additional runs (1 job per compute node) with different benchmarks (load in the figure) concurrently. Each job wrote data to three Lustre storage servers, each equipped with two HDDs. A factor of 2 indicates that the reference job took twice as long to complete under the additional load.

Figure 5 shows different mixes of synthetic (IOR and (numio) benchmarks in synchronous and asynchronous modes. All combinations show almost no overhead for up to three jobs running simultaneously, because their I/O fits three storage server connections. The 3x case (four jobs total)

![](_page_4_Figure_0.png)

Fig. 6: Normalized execution times of identical runs of numio and IOR, without additional (ref) and with additional 1 to 9 instances of the same program, varying the write frequencies (higher frequencies corresponding to more data).

![](_page_4_Figure_2.png)

Fig. 7: IOR and sync numio writing to 3 and 5 storage servers (S) with up to 9 concurrent jobs.

shows up to factor 1.5 overhead for IOR with IOR load representing the synthetic peak run and almost a quarter of that for numio reference with numio synchronous load. The highest load of 9 shows the largest difference between IOR and numio sync: factor 3.4 and 2.5 overhead, respectively. These cases could represent a peak and heavy load ensembles and their differences are not very surprising. For the numio ensembles, however, the async modes performed significantly worse, while the runtime of a single async run on the empty system was about 20% better than the sync run (120 to 98 seconds). This is most likely due to the fact that asynchronous I/O is stretched over the entire runtime of the job and overlaps with the extra jobs at almost any point in time, thus slowing each other down. Synchronous runs settle better and allow jobby-job alternating I/O, resulting in better overall performance, especially on the spinning disks used here.

In Figure 6, the second test compares IOR with IOR and numio async with numio async loads while writing varying amounts of data. For numio, the write frequency was adjusted and IOR wrote the corresponding amount of data. Of all the numio settings tested, the async case showed the worst performance, although it still significantly outperformed every IOR setting. Notably, even in the 3x case (four jobs in total), IOR showed a significant drop in performance. While the heaviest load (9x) factors remained nearly constant for all IOR jobs, they increased for numio ensembles with larger amounts of data due to less computation, thereby stretching I/O phases.

Figure 7 compares IOR and sync numio with the same type of load and data striped across three and five servers. Note that the reference runs on an empty system took the same time with three and five servers. However, the system can compensate for more additional numio than IOR runs for both configurations. Suppose the compute center needs to run one job per node at a time (ten in total) with a maximum performance degradation of 2.5x compared to an empty system run (9x to ref). In this case, the IOR ensemble states that five storage servers are required, while the numio ensemble would only require three servers, proving to be sufficient. Therefore, more accurate system benchmarking can help in making economic decisions. The numio settings chosen here correspond to a reasonably realistic I/O stress test scenario. All ensembles will most likely show even larger differences with a more balanced I/O load on larger scales.

*Findings: It is evident that various overlapping modes impact the coordination of shared system components. Additionally, employing a more realistic benchmark enables a more precise evaluation of system performance under heavy loads compared to relying solely on synthetic peak performance benchmarks.*

## *B. Compression*

An AMD-based system with Epyc processors featuring 32 cores and 256 GiB RAM per node was utilized in the section. Tests were conducted using a 1 Gb/s Ethernet interconnect, providing a real throughput of 117 MB/s. A patched Lustre was configured with a ZFS backend and a 1 MiB stripe size. We performed the test on a network that was significantly slower than the device throughput (N<<D) configuration, representing an oversubscription of the server's network bandwidth compared to the device's throughput.

We have run numio using 4 processes which first write a shared 3 GiB file and then perform further iterative calculations. This specific pattern is being closely analyzed as a representative segment of the recurring computation and writing behavior. Since each client has its own local view of the data, we can assume the behavior to be consistent across multiple clients. For the measurements, we have analyzed three different I/O modes exemplary using the MPI-IO backend.

In this scenario, we are examining a situation where data undergoes compression within the system. To illustrate, we are employing a custom prototype within Lustre, capable of supporting client-side compression, and interfacing with ZFS, which already possesses server-side compression capabilities. ZFS is not compressing the data a second time in these tests. We used for the LZ4 algorithm and attained a compression ratio of 6.43. Using numio, we are able to gauge distinct phases and have assessed the effective throughput per phase, derived from both the compressed data volumes and runtime, both comprehensively and for each I/O phase. We are noticing varied behaviors in the respective synchronization operations, all while keeping a close watch on CPU consumption.

Our benchmark offers a comprehensive evaluation of compression techniques, comparing server-side compression, which imposes no CPU overhead on the client and thus does not disrupt the application, with client-side compression, which competes for resources with the application. These methods are contrasted with a scenario where no compression is applied.

![](_page_5_Figure_0.png)

Fig. 8: Comparison of different synchronizations modes and different compression locations for a slower network that disk I/O and high compression ratio.

In the case of asynchronous compression, it is evident that the overall throughput correlates with the highest CPU costs. Similarly, in synchronous compression scenarios, the appearance of synchronicity masks an underlying asynchronous element. When data is transferred over the network, the call returns, allowing the application to continue its computations.

In situations involving ZFS, although CPU load remains comparably low as in uncompressed scenarios, throughput does not increase significantly due to the network remaining the bottleneck. Consequently, the application was not CPUbound and is not suffering by client-side compression while network an benefit.

*Findings: Compression introduces an additional layer of asynchrony, influencing CPU utilization, network performance, and consequently, directly affecting all layers when executed on the same resources as the primary application. The interaction is even more complex than in common asynchronous I/O case.*

#### *C. Network Congestion*

As mentioned in Section II-C, the network is a shared resource that is often used simultaneously by I/O streams and interprocess communication. While I/O networking aims for optimal throughput, inter-process communication is latency sensitive. Depending on the network configuration, these streams can quickly interfere with each other. We examine a real case from a large data center with a complex multi-layer network architecture. The network infrastructure is designed as a fat tree, with three levels created by the switches. In simple terms, all neighboring computing nodes connected to the branches from level two and above can be considered as

![](_page_5_Figure_7.png)

Fig. 9: Possible communication ways between 2 compute nodes in different cells of the fat tree.

![](_page_5_Figure_9.png)

Fig. 10: Detection of network congestion using numio. After implementation of virtual lanes, neither *case A* nor *case B* influence the runtime of numio anymore.

computing cells, resulting in varying routes between any two nodes. The file system is designed to be broad and uniform across level one, ensuring that all cells are evenly distributed. When a job requires compute nodes from multiple cells, the transfer is made through a higher switch level as shown in Figure 9. This network route can be traversed by multiple compute cells and the entire parallel file system concurrently.

We simulate a scenario in which a job with excessive I/O patterns can have a toxic effect on other jobs, especially those with significant interprocess communication. This phenomenon can only be effectively uncovered by using an ensemble of various benchmarks. In our setup, a single-node job floods the entire network with numerous large requests while another job concurrently performs parallel computations. For reference, we examine two examples of pairwise and collective communication involving 128 processes distributed across two compute nodes, with one node running in the same cell as the job causing network congestion. We also include a run with an additional I/O component to investigate the extent of mutual interference between I/O streams. We examined two variants of toxic I/O jobs. The first scenario A contained about 3,000 files of various sizes ranging from 100 MB to 7 GB, striped with -1 across all OSTs (160). The second variant B consisted of 365 files, each 167 GB in size, striped with progressive file layout (PFL) across 16 OSTs.

The tested scenario involves 35,000 iterations using a matrix of about 1 GB, with pairwise exchanges of about 190 kB between processes during each iteration. We evaluate three test cases: a baseline run as described, a Coll run that includes an additional exchange of a 265 kB buffer using an Allgather operation every 70 iterations, and a run where the matrix

![](_page_6_Figure_0.png)

Baseline (2s)

Fig. 11: Vampir traces for selected measurments. Green computation, red communication (MPI), blue I/O.

is flushed after every 200 iterations. For the latter run, we examine both blocking (sync) and non-blocking (async) MPI-IO backends. The toxic I/O job performs concurrent read requests on all data sets from one compute node calculating their checksums via md5sum. The client's 100 Gb/s limited network connection is overwhelmed by the incoming traffic from 40 (*Case A*) or 4 (*Case B*) servers at 200 Gb/s each, resulting in network congestion. This use case is commonly seen either for the actual checksumming required in tape archiving or as a representative scenario for post-processing workloads.

Figure 10 shows the measured values for toxic traffic *case A*, revealing a significant runtime delay in the baseline run. The introduction of additional collective communication exacerbates this delay, as expected. However, the behavior of I/O participation remains almost unaffected, as the delay can be attributed to the differences observed in the baseline run.

For the I/O test, despite the large influx of data, the file system still efficiently handles the smaller I/O requests. The latency delay caused by the saturated network has a much smaller impact on overall performance compared to the duration of disk I/O.

The toxic *case B* (involving fewer, larger files) shows a more concerning trend. Despite being distributed across a smaller number of OSTs, the larger packet sizes appear to be significantly congesting the network.

To support our assumption, a careful examination of the Vampir traces in Figure 11 confirms that latency-sensitive communication is strongly affected by the delay, which propagates further like an idle wave. A closer look reveals that the wave originates at the node (and in our case cell) boundary, precisely at process 64. These initial delays are significant enough to considerably hamper the application, resulting in a sustained negative impact on its performance.

Nevertheless, the I/O-intensive test case does not show any observable impact at the moment. Only the asynchronous test shows a noticeable degradation in I/O performance, which cannot be attributed solely to the baseline delay. It appears that the background I/O struggles to achieve effective overlap in the presence of a congested network. However, even with the additional delay caused by the load, the overall runtime still outperforms the pure time taken for synchronous I/O (async 183 s under toxic load compared to 200s sync without load).

In another scenario, not visualized here, we reduced latencies and extended computation time by increasing the matrix size to 60,000 rows with 200 iterations. In the Coll case, data sets of 512 KiB were exchanged every 5 iterations. As a result, the sensitivity to latency was mitigated, leading to a reduced load on the application. Although traces still indicated the presence of idle waves, the intervals between them were several seconds apart, in contrast to the fractions of seconds observed in the displayed scenario.

To verify our findings, we ran the same tests on separate cells far away from the toxic cell and could not see any delays in any of the tests. After identifying the problem described above, a virtual network lane was implemented that intelligently separates I/O and inter-node traffic. Subsequent measurements provided solid evidence of the measure's effectiveness in improving overall efficiency.

*Findings: We have effectively utilized our benchmark and ensemble strategy to demonstrate the presence of a complex negative interaction when utilizing a shared resource on the given system. Utilizing realistic scenarios enables us to make a more accurate assessment of whether the delays warrant any required actions, in contrast to ensembles composed of synthetic peak benchmarks. Due to cost and efficiency considerations, we refrained from measuring synthetic benchmarks during the operation of a large-scale computer, as it would require interfering with its ongoing processes. Such synthetic benchmarks typically represent worst-case scenarios.*

#### V. CONCLUSION

The use of real, rather than emulated, computation phases allows more realistic application behavior to be replicated. Combined with an ensemble benchmarking strategy, this makes it possible to uncover even complex negative interactions that occur when using a shared resource such as the file system or network. This allows for a much more objective evaluation of the systems.

We were able to demonstrate non-trivial effects of the overlap of compression, computation and I/O phases on the overall runtime of an application. This is exacerbated by the interaction of multiple applications that perform differently under the same total I/O load as the IOR runs, allowing for a more accurate estimation of busy system performance. Data center operators need representative benchmarks such as numio to make economic decisions that better reflect the actual user environment, especially when numio is tuned to the user software.

*a) Acknowledgments:* This work used resources of the Deutsches Klimarechenzentrum (DKRZ) granted by its Scientific Steering Committee (WLA) under project ID ku0598. We want to thank Niclas Schroeter for helping out with creating the numio benchmark.

#### REFERENCES

- [1] I. B. Peng, S. Markidis, E. Laure, G. Kestor, and R. Gioiosa, "Idle period propagation in message-passing applications," in *2016 IEEE 18th International Conference on High Performance Computing and Communications; IEEE 14th International Conference on Smart City; IEEE 2nd International Conference on Data Science and Systems (HPCC/SmartCity/DSS)*, 2016, pp. 937–944.
- [2] A. Afzal, G. Hager, and G. Wellein, "Propagation and decay of injected one-off delays on clusters: A case study," in *2019 IEEE International Conference on Cluster Computing (CLUSTER)*, 2019, pp. 1–10.
- [3] ——, "The role of idle waves, desynchronization, and bottleneck evasion in the performance of parallel programs," *IEEE Transactions on Parallel and Distributed Systems*, vol. 34, no. 2, pp. 623–638, 2023.
- [4] T. Li, S. Byna, Q. Koziol, H. Tang, J. L. Bez, and Q. Kang, "h5bench: HDF5 I/O Kernel Suite for Exercising HPC I/O Patterns," 2021.
- [5] D. Skinner and W. Kramer, "Understanding the causes of performance variability in hpc workloads," in *IEEE International. 2005 Proceedings of the IEEE Workload Characterization Symposium, 2005.* IEEE, 2005, pp. 137–149.
- [6] Z. Xue, G. Shen, J. Li, Q. Xu, Y. Zhang, and J. Shao, "Compression-aware I/O performance analysis for big data clustering," in *BigMine*. ACM, 2012, pp. 45–52.
- [7] M. Kuhn, J. M. Kunkel, and T. Ludwig, "Data Compression for Climate Data," *Supercomput. Front. Innov.*, vol. 3, no. 1, pp. 75–94, 2016.
- [8] S. Liu, X. Huang, Y. Ni, H. Fu, and G. Yang, "A High Performance Compression Method for Climate Data," in *ISPA*. IEEE Computer Society, 2014, pp. 68–77.
- [9] P. Fernando, S. Kannan, A. Gavrilovska, and K. Schwan, "Phoenix: Memory Speed HPC I/O with NVM," in *HiPC*. IEEE Computer Society, 2016, pp. 121–131.

- [10] V. Venkatesan, M. Chaarawi, E. Gabriel, and T. Hoefler, "Design and Evaluation of Nonblocking Collective I/O Operations," in *EuroMPI*, ser. Lecture Notes in Computer Science, vol. 6960. Springer, 2011, pp. 90–98.
- [11] [Online]. Available: https://netlib.org/linpack/
- [12] [Online]. Available: https://hpcg.info/
- [13] S. Breuner, "Breuner/Elbencho: A distributed storage benchmark for file systems, Object Stores & block devices with support for gpus." [Online]. Available: https://github.com/breuner/elbencho
- [14] J. Kopec, "Evaluating Methods of Transferring Large Datasets," in SCFA, ser. Lecture Notes in Computer Science, vol. 13214. Springer, 2022, pp. 102–120.
- [15] D. G. Chester, T. L. Groves, S. D. Hammond, T. Law, S. A. Wright, R. P. Smedley-Stevenson, S. A. Fahmy, G. R. Mudalidge, and S. A. Jarvis, "Stressbench: A configurable full system network and I/O benchmark framework," in *2021 IEEE High Performance Extreme Computing Conference, HPEC 2021, Waltham, MA, USA, September 20-24, 2021*. IEEE, 2021. [Online]. Available: https://doi.org/10.1109/ HPEC49654.2021.9774494
- [16] K. Chasapis, J. Vet, and J. Acquaviva, "Benchmarking Parallel File System Sensitiveness to I/O patterns," in *MASCOTS*. IEEE Computer Society, 2019, pp. 427– 428.
- [17] S. Neuwirth and A. K. Paul, "Parallel I/O Evaluation Techniques and Emerging HPC Workloads: A Perspective," in *CLUSTER*. IEEE, 2021, pp. 671–679.
- [18] M. Dorier, S. Ibrahim, G. Antoniu, and R. B. Ross, "Using Formal Grammars to Predict I/O Behaviors in HPC: The Omnisc'IO Approach," *IEEE Trans. Parallel Distributed Syst.*, vol. 27, no. 8, pp. 2435–2449, 2016.
- [19] C. Wang, K. Mohror, and M. Snir, "File System Semantics Requirements of HPC Applications," in *HPDC*. ACM, 2021, pp. 19–30.
- [20] B. Wadhwa, A. K. Paul, S. Neuwirth, F. Wang, S. Oral, A. R. Butt, J. Bernard, and K. W. Cameron, "iez: Resource Contention Aware Load Balancing for Large-Scale Parallel File Systems," in *IPDPS*. IEEE, 2019, pp. 610–620.
- [21] A. K. Paul, A. Goyal, F. Wang, S. Oral, A. R. Butt, M. J. Brim, and S. B. Srinivasa, "I/O load balancing for big data HPC applications," in *2017 IEEE International Conference on Big Data (Big Data)*, 2017, pp. 233–242.
- [22] B. Yang, Y. Zou, W. Liu, and W. Xue, "An End-to-end and Adaptive I/O Optimization Tool for Modern HPC Storage Systems," in *IPDPS*. IEEE, 2022, pp. 1294– 1304.
- [23] T. Henretty, K. Stock, L. Pouchet, F. Franchetti, J. Ramanujam, and P. Sadayappan, "Data Layout Transformation for Stencil Computations on Short-Vector SIMD Architectures," in CC, ser. Lecture Notes in Computer Science, vol. 6601. Springer, 2011, pp. 225–245.

