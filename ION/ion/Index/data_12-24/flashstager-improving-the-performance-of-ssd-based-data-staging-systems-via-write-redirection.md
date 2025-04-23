# FlashStager: Improving the Performance of SSD-based Data Staging Systems via Write Redirection

Xuechen Zhang School of Engineering & Computer Science Washington State University Vancouver xuechen.zhang@wsu.edu

Fang Zheng IBM Research zhengfan@us.ibm.com

Karsten Schwan, Matthew Wolf School of Computer Science Georgia Institute of Technology {schwan, mwolf}@cc.gatech.edu

*Abstract*—When SSDs are used for in-situ execution of dataintensive scientific workflows, it is challenging to obtain consistently high I/O throughput because its I/O efficiency can be compromised for serving write and read requests simultaneously. This issue is so-called *write-read interference*. In this paper, we propose a novel scheme named FlashStager, which can isolate writes from reads using *write redirection* to improve data staging performance of SSDs by minimizing the write-read interference. Not only can it detect the interference, but also evaluate whether it is cost-effective to resolve it by executing the write redirection according to its correlation with write ratio and request size. Our experiments with both micro-benchmarks and real scientific applications show than FlashStager can improve I/O performance of staging by 40% on average.

## *Keywords*-I/O Staging, SSDs, and Write-read Interference.

### I. INTRODUCTION

To fill the large performance gap between DRAMs and hard disks (HDDs), flash-based storage devices, e.g., solidstate disks (SSDs), are becoming widely employed in highperformance computing (HPC) systems because SSD's performance is much less sensitive to random access than that of HDD, while its cost per GB is lower than that of DRAM. Researchers are studying different strategies to fit SSDs into the memory hierarchies of HPC clusters. An important one of them is using SSDs on staging nodes as data buffers [1] so that less data needs to be transferred from compute nodes to HDD-based parallel file systems, leading to reduction in energy consumption and better I/O performance. For example, GTS [2] for fusion simulation can write checkpointing and snapshot data to a node-local or distributed staging buffer. Concurrently, its analytics may read data from the buffer for physics diagnostics or visualization in situ.

We conducted experiments to reconcile past observations about I/O characteristics of SSDs in the context of data staging workloads issuing a mix of writes and reads. Our results indicate that 1) when they are served concurrently on SSDs, *write-read interference* may occur. Because of the interference, SSD's performance can be significantly reduced by up to 72%—in I/O throughput; 2) SSD's performance under the interference is strongly correlated with *write ratio* and *request size*. Previous work about I/O staging using SSDs has completely ignored the above issues. Recent system research provides low-level solutions to resolving write-read interference. For example, erase suspension [3] may help reduce read latency, but it requires changes of hardware interface, which is not possible for commercial SSD products already installed in existing HPC systems. The FIOS [4] I/O scheduler and Rails [5] tend to solve a similar issue in Linux OS. However, they are not applicable to distributed data staging systems and especially difficult to be adopted for machines running customized OSs, e.g., UNICOS [6] of Cray systems.

For better adaptability we propose a novel approach *write redirection* for data staging on SSDs to minimize write-read interference. Specifically, if the interference is detected on a SSD, write requests can be redirected to other SSDs in the system to explore I/O efficiency. We implemented a distributed staging system FlashStager as I/O middleware with the support of write redirection. It can quantitatively evaluate whether it is cost-effective to execute write redirection according to request size and write ratio measured at runtime. We design algorithms, comprising FlashStager, to coordinate data staging among distributed SSDs so that workload balance can be achieved without sacrificing I/O efficiency and affecting the execution of compute-bound applications and analytics.

FlashStager is implemented in the ADIOS software [7], leveraging its standard I/O interface and proven adaptability in large-scale HPC systems. It also uses minor support from the operating systems for measurement of I/O patterns on SSDs (e.g., write ratio). We evaluated an implementation of FlashStager using both synthetic workloads and a real scientific workflow GTS and its analytics. The comprehensive evaluation shows that FlashStager can reduce the data staging time by 40% and the total execution time of the applications by 31% on average.

### II. DESIGN OF FLASHSTAGER

FlashStager is designed to use *write redirection* to reduce write-read interference and improve I/O performance of SSDs for staging. To make the approach truly effective there are several questions to be answered in the design. First, how to detect write-read interference? Second, where to redirect writes under interference in a distributed staging system without sacrificing workload balance? Third, how to effectively solve issues caused by write redirection, e.g., file fragmentation? In this section we describe the architecture of FlashStager and the management of staging requests and data fragments to answer these questions.

![](_page_0_Picture_17.png)

![](_page_1_Figure_0.png)

Fig. 1: Architecture of FlashStager

We implement FlashStager in ADIOS [7] leveraging its standard interface and its proven adaptability. The modification to the existing software is in the form of adding a new I/O transport. FlashStager has four major components, FlashStager-client, FlashStager-server, I/O-monitor, and Staging-manager. FlashStager-client exposes a standard I/O interface to applications and issues I/O requests from compute to staging nodes. FlashStager-server receives requests and issues them to local storage systems, e.g., SSDs. I/O monitor collects I/O access pattern (e.g., write ratio, request size, and disk seeking distance) and CPU consumption for serving write requests from different applications. These profiling data are passed to Staging-manager. Disk seeking distance is used to quantify sequentiality of staging workloads [8]. Stagingmanager then makes a write redirection plan for data staging and passes it to both FlashStager-server and FlashStagerclient for execution by destroying existing connections and establishing new connections as illustrated in Figure 1.

To remove the interference, an algorithm is designed to detect when an application should choose another SSD for data staging considering both the interference intensity and availability of staging nodes. We quantify the interference as a ratio R of throughputopt and throughputcurrent, where throughput pt is the optimal I/O throughput as if the interference were resolved and is related to request size and access pattern of workloads, and throughputcurrent is calculated online by accessing /proc/diskstats. If R is larger than a predefined threshold ratiosystem. Staging-manager will investigate the case and make a new plan of data staging. After the write-read interference is detected, FlashStager can solve the problem by isolating writes from reads on the staging nodes. To achieve this, write requests should be redirected from a source node to a target node. FlashStager chooses the target nodes that have have adequate CPU resource to serve additional I/O requests. In addition, the redirected workloads should not cause write-read interference on the target nodes.

With write redirection output files of applications may be composed of a number of small data fragments stored on multiple staging nodes. After redirection the locations of the fragments being written are recorded in a distributed mapping table. A write request from an application will be served on a

staging node, initially selected by FlashStager in a round-robin order. If write-read interference is detected, a write request will be served on a node specified in a redirection plan determined by Staging-manager. After receiving an acknowledgement of successful writes, FlashStager-client will insert/update an entry in the mapping table. For serving a read request FlashStager needs to find the address of the fragment that stores the requested data. To speed up the lookup, addresses of fragments are managed in a search tree. If the fragment is found, the corresponding entry in the mapping table will be further read to provide the address of requested data in the staging file and contact information about the staging node.

#### III. PERFORMANCE EVALUATION

FlashStager was prototyped and evaluated on the Sith cluster at Oak Ridge National Laboratory. The cluster includes 40 32-core (8 cores by 4 sockets) 2.3 GHz AMD Opteron(tm) Processor 6134 nodes running Redhat Linux of kernel-2.6.32. All nodes are interconnected with a dual-rail 4X ODR Infiniband network having 40 Gb/s data rate. Each node is also configured with 64 GB DRAM and a software raid (RAID0) consisting of three 512 GB Samsung SSDs (840 PRO Series) with 512 KB chunk size. In the experiments, variable number of nodes are set up as compute nodes or staging nodes. All the nodes share a site-wide parallel file system Atlas running Lustre [9]. To evaluate staging performance on SSDs, we set the size of staging buffers in memory to be 1 MB so that most of staging data can be stored on SSDs and ratiosystem to be 1.6 as the threshold in the following experiments.

array bench (micro-benchmark): It is a staging-I/O benchmark and developed based on the example codes in ADIOS [7]. It is designed to simulate I/O patterns with multiple writers and readers exchanging matrix (array) data using SSDs as staging storage devices. The writers compute on arrays and then write them out to SSDs. The readers read the data back immediately they are available and continue the computation for data analysis. Reader processes can be blocked if writer's data are not available. Array dimension N is configurable in the benchmark. Another parameter which is the key to the I/O performance of staging systems is staging ratio. We can set it in the form of n : 1. If n is equal to 1, it is a 1:1 mapping between writers and readers. Therefore, array_bench executes the same number of writers and readers for testing I/O performance of staging workloads. If n is set larger than 1, then the benchmark will create a number of writers and readers according to the staging ratio and the total number of processes specified in a job script. After the staging data being written, the readers will need to create a single array to host n pieces of the writer data (sub-arrays) automatically for analysis. We use direct I/O and set request size to 16 KB for the benchmark when it accesses SSDs.

GTS (macro-benchmark): The GTS petascale application is a particle-in-cell code designed for studying turbulent transport in magnetic fusion plasmas. Multiple arrays are computed and written in its I/O phases for physics diagnostics, visualization, and/or checkpointing. GTS is written in Fortran.

![](_page_2_Figure_0.png)

Fig. 2: Execution times of array_bench with different staging approaches. The size of staging data is increased from 128 * 128 to 1024 * 1024.

For writing staging data, we rewrite multiple functions in the GTS code to use FlashStager for staging. For example, restart write() is modified for staging the zion array, which contains the pase space coordinates of all the simulated ion particles, and the phi array, which contains the grid-based electrostatic potential field. For reading the staging data, we instrument a program called fft_analysis, which is one of the most heavily used analytics for GTS. It is performed to calculate the particles' spatial distribution based on the zion arrays, and to execute Fourier transforms for physical diagnosis on the phi arrays.

### A. Micro-benchmark Results

We first evaluate FlashStager with the micro-benchmark array_bench. In the following experiments, we use the default setting for this benchmark with 10:1 for staging ratio unless otherwise specified.

We first increase the dimension N of arrays from 128 to 1024. Figure 2 shows the execution times of the benchmark in both the vanilla system and that using FlashStager. We have the following observations for this. First, when the dimension N is 128, the execution times of the benchmark are 49s and 50s, respectively. This is because OS buffer cache plays a key role in serving the staging I/O requests asynchronously, making SSD's performance have a trivial impact on the execution time of the benchmark. Second, there is about 2% overhead for using FlashStager, which is caused by extra operations of monitoring I/O patterns of the workload. Third, when the dimension N of arrays is increased to 1024, buffer caches on staging nodes were quickly saturated. Therefore, most of the staging requests were served on the SSDs, whose I/O throughput becomes a critical factor in the determination of the execution time of array_bench.

Furthermore, we have shown instantaneous I/O throughput of SSDs in every time window during the execution in the vanilla system on one node of the Sith cluster (Sith4) in Figure 3(a). The size of a time window is 1 second. The throughput was measured using iostat. We can observe that its throughput varies from 146 MB/s to 496 MB/s. And the period between two peaks is about 120s, during which the effective bandwidth of SSDs plummets because of the writeread interference on the SSDs. As a result, when the dimension N is increased to 1024, the execution time of array_bench

![](_page_2_Figure_7.png)

Fig. 3: (a) Instantaneous I/O bandwidth of SSDs measured using iostat without redirection. (b) I/O bandwidth of SSDs with redirection using FlashStager. Write redirection from the original host to the new host happened at 265th second.

![](_page_2_Figure_9.png)

Fig. 4: SSD I/O times and total execution times of array_bench with different staging ratios.

is highly increased to 4980s. In comparison, the execution time is 1273s with FlashStager. The reason is illustrated in Figure 3(b). FlashStager detected the interference for write redirection to a new host Sith3 at t = 265s. After write redirection, the read requests started to be served at a stable throughput which is 430 MB/s for the program. As a result, the redirection cost is well amortized over the remaining period of the program's execution.

In the second experiment we evaluate FlashStager as the staging ratio is increased from 10:1, 20:1, to 30:1. The dimension N of arrays is set to 512. A higher staging ratio implies that a single reader has to read more data from SSDs for every time step. And there will be less read processes and more write processes in the system. The total execution time of the benchmark consists of networking time and SSD I/O time. The latter and total execution times are shown in Figure 4. We can observe that on average I/O times with FlashStager is reduced by 39%, and the total execution time by 31% compared to the vanilla system. This is because FlashStager can effectively detect write-read interference on the SSDs and resolve it by write redirection. Another observation is that when the ratio

![](_page_3_Figure_0.png)

Fig. 5: Instantaneous arrival rates of reads during the execution of array bench with 10:1 or 30:1 staging ratio.

![](_page_3_Figure_2.png)

Fig. 6: Total execution times of the GTS benchmark configured with different number of particles in a cell. (a) One checkpoint after every time step. (b) One checkpoint per five time steps.

is 30:1, the benchmark in the vanilla and FlashStager system have similar execution times. The reason is that the write-read interference with a 30:1 staging ratio is less significant for FlashStager to trigger write redirection. In this scenario, it has much smaller number of readers, which can issue read requests concurrently with writers, leading to less interference on the SSDs. We confirm this by measuring the arrival rates of read requests on a staging node. As shown in Figure 5, when the staging ratio is 30:1, the maximal arrival rate is three times smaller than the rate when the ratio is 10:1. Therefore, I/O efficiency on SSDs did not change dramatically to be captured by FlashStager for optimization using write redirection.

## B. Macro-benchmark Results

We evaluated FlashStager with the GTS macro-benchmark, which has interleaved computation and I/O during its execution. Particularly, two data arrays, phi and zion are selected for staging. They are eventually stored in a file called 'restart' for the purpose of checkpointing and post-analysis. phi contains the grid-based electrostatic potential field, while zion contains the pase space coordinates of all the simulated ion particles. In the experiment, we run the GTS benchmark on the Sith cluster with 256 parallel processes and 32:1 staging ratio. The number of particles per grid cell is increased from 5, 10, 15, to 20. Accordingly, the amount of staging data is also increased from 908 MB to 3.6 GB when the checkpointing operation is conducted for every time step. After readers, e.g., analytics, receive all the data from multiple writers, they will prepare the data for further analysis using Fourier transforms. We also change the frequency of checkpointing operations to study its impact on I/O efficiency of SSDs.

Figure 6(a) and (b) show the execution times of the GTS benchmark. We can have following observations from the figures. First, checkpointing frequency significantly affects the execution time of GTS. For the most I/O-intensive setting, which has 20 particles in a cell, the execution time with a high checkpointing frequency is 24% longer than that with checkpointing being done less frequently. Second, in both of the cases, computing time takes a significant part of total execution time of the benchmark, making the performance improvement from using FlashStager is not as significant as those showed with the array_bench benchmark, which does not have a compute kernel. Even though I/O time does not take a significant ratio of the total execution of GTS, FlashStager can still help improve I/O efficiency on SSDs and reduce its total execution time by up to 12%. Third, the more particles in a cell. the more improvement we can have by using Flash-Stager. This is because its I/O time becomes an increasingly significant factor in determining the total execution time of the GTS benchmark.

## IV. CONCLUSION

We presented FlashStager, an I/O middleware layer that can monitor write-read interference and automatically solve the issue by isolating writes from reads via write redirection in distributed data staging systems. FlashStager was designed to optimize staging performance by balancing workloads on staging nodes and coordinating request service for higher I/O efficiency. FlashStager is implemented in the ADIOS library for its adaptability and compatibility. Our experimental evaluation with both synthetic workloads and the scientific application GTS shows that FlashStager can reduce the I/O time by 40% and the total execution time of the applications by 31% on average.

#### V. ACKNOWLEDGEMENTS

We would like to thank our collaborators Stephane Ethier at Princeton Plasma Physics Laboratory for sharing us their scientific applications. This work was supported in part by the National Science Foundation under grant ACI-1565338.

#### REFERENCES

- buffer https://www.nersc.gov/users/ [1] "Burst at nersc.' computational-systems/cori/burst-buffer/.
- [2] K. Madduri, K. Ibrahim, S. Williams, E. IM, S. Ethier, J. Shalf, and L. Oliker, "Gyrokinetic toroidal simulations on leading multi- and manycore hpc systems," in SC'11, 2011.
- [3] G. Wu and X. He, "Reducing ssd read latency via nand flash program and erase suspension," ser. FAST'12, 2012.
- [41 S. Park and K. Shen, "Fios: A fair, efficient flash i/o scheduler," in Proceedings of the 10th USENIX Conference on File and Storage Technologies, ser. FAST' 12, 2012.
- [5] D. Skourtis, D. Achlioptas, N. Watkins, C. Maltzahn, and S. Brandt, "Flash on rails: Consistent flash performance through redundancy," ser. USENIX ATC' 14, 2014.
- [6] "Cray xt3 supercomputer datasheet," http://www.craysupercomputers. com/downloads/crayxt3/crayxt3_datasheet.pdf.
- [7] "Adios: the adaptable io system," http://www.olcf.ornl.gov/centerprojects/adios/.
- X. Zhang and S. Jiang, "Interferenceremoval: Removing interference of [8] disk access for mpi programs through data replication." ser. ICS '10.
- [9] Lustre Software Release 2.x Operations Manual, http://lustre.org/ documentation/.

