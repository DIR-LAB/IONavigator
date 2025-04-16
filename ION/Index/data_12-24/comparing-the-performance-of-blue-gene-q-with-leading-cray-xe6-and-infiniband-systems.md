# **Comparing the Performance of Blue Gene/Q with Leading Cray XE6 and InfiniBand Systems.**

Darren J. Kerbyson, Kevin J. Barker, Abhinav Vishnu, Adolfy Hoisie Performance and Architecture Lab (PAL), Pacific Northwest National Laboratory, USA {Darren.Kerbyson,Kevin.Barker,Abhinav.Vishnu,Adolfy.Hoisie}@pnnl.gov

*Abstract***—Three types of systems dominate the current High Performance Computing landscape: the Cray XE6, the IBM Blue Gene, and commodity clusters using InfiniBand. These systems have quite different characteristics making the choice for a particular deployment difficult. The XE6 uses Cray's proprietary Gemini 3-D torus interconnect with two nodes at each network endpoint. The latest IBM Blue Gene/Q uses a single socket integrating processor and communication in a 5-D torus network. InfiniBand provides the flexibility of using nodes from many vendors connected in many possible topologies. The performance characteristics of each vary vastly along with their utilization model. In this work we compare the performance of these three systems using a combination of micro-benchmarks and a set of production applications. We also discuss the causes of variability in performance across the systems and quantify where performance is lost using a combination of measurements and models. Our results show that significant performance can be lost in normal production operation of the Cray XE6 and InfiniBand Clusters in comparison to Blue Gene/Q.** 

*Keywords-High Performance Computing, Performance Evaluation, Performance Modeling, Application Analysis* 

#### I. INTRODUCTION

Three types of systems currently dominate the list of the most powerful supercomputers – namely those by Cray, IBM and clusters built using InfiniBand. Each differs in architecture at all levels from the individual processor cores to full system topology. Each exhibits different performance characteristics in their sub-systems (processor-core, memory, communication) and each is packaged in different ways to allow scaling to high node counts enabling massive levels of parallelism. However, they have one thing in common, they each aim to achieve high performance on the all-important workload they process.

In this work we evaluate the latest Blue Gene - BG/Q system from IBM and compare it against current Cray XE6 and InfiniBand systems. This is the first work that we are aware of that provides a performance comparison of BG/Q with other leading systems from an actual empirical performance analysis using production applications as well as micro-benchmarks.

The Cray XE6 and its associated XK6 accelerated version are the first systems to use the Gemini network in a 3-D torus topology [1]. They utilize commodity processors which, to date, have been from AMD. Large-scale installations include Cielo at Los Alamos, Hopper at NERSC, Titan at Oak Ridge.

Blue Gene/Q (BG/Q) is the third generation of IBM's Blue Gene architecture [2,3,4]. A key characteristic of the Blue Gene architecture has been that each node exhibits modest computational capabilities but a large number of nodes are used to achieve high performance. BG/Q however increases the pernode core count over the previous generation system from four to 16 with an increased clock speed of 1.6 GHz. This year has seen the installation of the 20PF Sequoia system at Lawrence Livermore and the 10PF MIRA system at Argonne.

InfiniBand systems are a significant fraction of the top500 list. They enable flexibility for a system's topology and allow for the use of commodity nodes using Intel and AMD as well as other processors. The latest network from Mellanox, the fifth generation ConnectX-3, offers 4x FDR speeds [5]. Current large installations include Nebulae at Shenzhen Advanced Institute of Technology, and Pleiades at NASA Ames.

The primary contributions of this work are as follows:

- Analysis of the individual characteristics of each system using micro-benchmarks as well as applications that use significant fractions of computing time on current systems,
- Quantification of the performance lost due to production usage of each system using previously developed and validated performance models,
- Demonstration of the efficiency of Blue Gene/Q scaling: the performance of a single BG/Q node is lower than an Intel or AMD node, but at larger scales this is reversed due to low OS noise and lack of inter-job interference.

This work provides an interesting insight into the impact of system architectural decisions on overall application performance. Of direct relevance are single-core and singlenode performance, communication topology, and the systems methodologies for mapping logical tasks onto physical hardware resources. As an example, we quantify the degree to which task interaction caused by the Cray XE6's job allocation strategy impacts application scaling behavior, and how this contrasts with Blue Gene's strategy in which jobs are isolated from one another with predictable results. Our work thus offers realistic insights into the performance of these systems.

Section II provides an overview of the three architectures. The performance characteristics of the systems are compared in Section III, and a performance comparison using production applications is given in Section IV. Results are discussed in Section V and in particular quantify the variability and how much performance is being lost in the normal operation of these systems. Work closely related to our own is discussed in Section VI. Conclusions to this work are given in Section VII.

## II. ARCHIETCTIURE OVERVIEW

## A. *Cray XE6*

The XE6 is the latest in the line of 3-D mesh based systems from Cray and uses the Gemini network. It was introduced in 2010 and superseded systems that used the earlier Sea-Star network that was first used in Red-Storm [6]. At the heart of Gemini is Cray's 48-port YARC switch that is currently used

1521-9097/12 $26.00 © 2012 IEEE DOI 10.1109/ICPADS.2012.81

to construct a 3-D (XYZ) torus topology and will also form the basis for Cray's forthcoming systems that are built using with a dragonfly topology [7]. Four ports connect the ±Y-dimensions, eight ports interconnect each ±X and ±Z-dimensions with the remaining eight ports used to connect two local nodes.

Each compute node contains two sockets which can be either two AMD G34 based processors (Magny-Cours or Interlagos) or one AMD processor and an NVidia GPU. The latter is designated an XK6 node and systems containing both node types are possible. A single rack contains 96 nodes. The X dimension of the network is typically implemented across racks in the same row of a system, Z within a rack, and Y across racks within a column as well as within a rack [8].

In this work we utilize the Hopper system at NERSC [9]. Hopper consists of a total of 6,384 nodes connected in a 17824 topology. Each node contains a dual-socket 2.1 GHz AMD Magny-Cours. Each processor is a dual-chip module, a chip contais six processor-cores, a shared 6MB L3 cache, and a memory controller supporting two DDR3-1333 channels. The peak floating point performance per node is 201.6 GF/s (2 processors * 2 chips * 6 cores * 4 fp/cycle * 2.1 GHz). The peak inter-node communication rate in the *X & Z* dimensions is 9.375 GB/s and in Y is 4.68 GB/s. A total of 256 nodes (6,144 processor-cores) were used in this work and allocated through Hopper's normal production allocation system.

## B. *Blue Gene/Q*

Like its predecessors, BG/Q is implemented using a single chip containing both processor-cores and communication resources. Each BG/Q node has 17 functional cores but is manufactured with 18-cores with the specific aim to improve manufacturing yield. Each core is identical in functionality but through software core-specialization only 16 cores can be directly used by applications with the remaining one dedicated to running a light weight OS. Dedicating a core in this way enables offloading support activities and significantly reduces impact on application cores. Each processor core can execute a quad-vector double-precision floating-point operation per cycle (8-flops) and has a clock-rate of 1.6 GHz. All cores in a node share a 32MB L2 cache and two memory controllers that each support a DDR3-1333 memory channel. Each processor-core

has hardware support for four threads using 4-way Simultaneous Multi-Threading (SMT) with the aim to hide memory latency for certain applications.

Each node contains has 11 external ports, 10 are used to form a 5-D (*ABCDE*) torus network and one allows connection to an I/O node. Each communication channel has a peak of 2GB/s in each direction. Communication collectives and barriers are implemented using this 5-D network unlike previous Blue Genes that had separate dedicated networks.

A BG/Q system is built using 32 compute-nodes to a compute-drawer, 16 drawers to a mid-plane, and two midplanes to a rack. The size of the 5-D torus is fixed at various node counts no matter which nodes are allocated to a job. The fifth (E) dimension is always two wide and contained within a compute-card to minimize wiring. This work utilized a midplane of BG/Q with 512 nodes (8,192 processor-cores) and arranged in a 4444-2 5-D torus.

#### C. *Infiniband*

InfiniBand enables off-the-shelf compute nodes to be used with a variety of interconnection topologies, including fat-trees. InfinBand uses two components: a PCIe based NIC (typically one per compute node), and a 36-port crossbar switch that is packaged in a variety of ways from a 36-port "leaf" switch to a chasis containing several crossbars to form a 648-port switch.

The PIC cluster used in this work, sited at PNNL [10], contains 640 dual-socket AMD Interlagos compute-nodes and uses 4x QDR NICs and switches. Nodes are connected to a single 648-port Qlogic switch while others are connected directly to the Qlogic switch via 36-port leaf switches. The Qlogic switch contains a total of 54 36-port crossbars that are connected internally as a full fat-tree topology. The peak communication speed of each network channel is 40+40 Gb/s.

An Interlagos processor consists of a dual chip module, a chip contains four dual-core Bulldozer modules running at 2.1 GHz. Each module can issue two 128-bit wide or one 256-bit wide floating-point operation per cycle (8 flops per cycle). Each chip has a shared 8MB L3 cache and a memory controller supporting two DDR3-1600MHz channels. In this work we used 144 nodes (4,608 cores) of this system that are directly connected to the Qlogic switch with full fat-tree topology.

| System | Cray XE6 | IBM Blue Gene/Q | InfiniBand / AMD |
| --- | --- | --- | --- |
|  | NERSC - Hopper | Test system (1 Rack) | PNNL - PIC |
| Node count | 6,384 | 1024 | 640 |
| Core count | 153,216 | 16,384 | 20,480 |
| Memory (TB) | 212 | 16 | 41 |
| Peak Performance (Pflops/s) | 1.28 | 0.2 | 0.17 |
| Node |  |  |  |
| Processor type | AMD Magny-Cours | IBM PowerPC A2 | AMD Interlagos |
| Processor count | 2 | 1 | 2 |
| Core count | 24 | 16 | 32 |
| Clock speed (GHz) | 2.1 | 1.6 | 2.1 |
| DP Peak performance (Gflops/s) | 201.6 | 204.8 | 268.1 |
| Memory (GB) | 32 | 16 | 64 |
| Memory Speed | DDR3-1333 | DDR3-1333 | DDR3-1600 |
| Network |  |  |  |
| Network type | Cray Gemini | IBM Proprietary | InfiniBand 4X QDR |
| Topology | 3-D Torus (17824) | 5-D torus | full fat-tree |
| Link Peak Speed (GB/s/direction) | 9.375 (XZ), 4.68 (Y) | 2.0 (ABCDE) | 4.0 |

TABLE I. SUMMARY OF ARCHITECTURAL CHARACTERISTICS

## III. SYSTEM ALLOCATION AND PRODUCTION USE

The three systems differ in the way in which nodes are allocated to an application when in a normal production environment. Though we are not concerned with the form that a particular batch queuing system may take, we are concerned with the actual nodes allocated to a particular application job. The simplest case to consider is that of BG/Q in which the topology of the requested allocation is determined by its size and defaults to a known topology no matter which nodes in the system are actually allocated. This is very different to the case for both the Cray XE6 and the InfiniBand cluster where there is no guarantee on the locality or arrangement of nodes that are allocated. This should also be contrasted with the case of using a system in dedicated access mode in which full control of the mapping of application tasks to nodes is typically possible.

## A. *Cray XE6*

Nodes allocated to a job on a Cray XE6 are determined primarily by those available at the instant at which a job is launched. It is possible that the allocated nodes are logically close to each other, but they are just as often dispersed. In addition, the logical naming of nodes does not match the X-Y-Z ordering of network locations. This indirection needs also to be taken into account if an optimal topology-aware mapping of the application tasks to allocated nodes is to take place. Typically on production systems no such optimal mapping is available, and jobs are subject to both intra-job communication contention effects as well as inter-job interference. These effects can be rather large and can be exacerbated by the size of the network dimensions, especially in a 3-D torus (note that the size of the largest dimension on hopper is 24).

## *B. Blue Gene/Q*

Though the exact nodes that are allocated to a particular application on BG/Q may not be known in advance, the topology of the nodes is defined. This allows for the optimization of tasks-to-cores when the communication topology of the application is known in advance e.g. [11]. In addition, the nodes that are allocated are also self-contained in that they are not subject to inter-job interface apart from when using shared resources such as a common file-system.

#### C. *InfiniBand*

There are multiple ways that jobs can be allocated to nodes on InfiniBand clusters. This can range from scheduling a job using contiguous nodes that are connected to a single or set of crossbar switches to jobs that are spread out across the system. Using 36-port InfinBand crossbars in a full-fat tree topology it is possible for jobs of multiples of 18 nodes in size to fully utilize a set of crossbars, exhibiting high locality still possibly subject to contention within higher levels of the network by other jobs, and also possibly subject to intra-job interference depending on the routing strategy employed [12]. In the InfiniBand cluster used at PNNL, jobs were allocated using a subset of nodes within a three-rack partition of the system that contained 144 nodes in total.

All of the performance results presented below were obtained when the systems were in normal production operation. In this way we analyze the actual performance one would expect to see in normal use of the systems.

## IV. LOW-LEVEL PERFORMANCE CHARACTERISTICS

Prior to the analysis of application performance on any of the systems, our approach is to use microbenchmarks to examine separately important aspects of a system that have a direct impact on performance. In this section we examine the following aspects:

- Memory latency and bandwidth,
- OS noise [13],
- Intra- and inter-node point-to-point communication
- Collective communication performance, and
- Network congestion properties.

All the multi-node tests, including all communication tests as well as application analysis in Section V, were measured using five different allocations and five runs on each allocation on each system. Where appropriate the mean of the measurements are shown as well as their range (minimum and maximum).

## A. *Memory Performance*

The performance of the memory on each node of the systems was examined using the MPI version of the STREAM benchmark [14], to examine memory bandwidth, as well as a memory latency benchmark that accessed separate cache-lines in a large-data vector in such a way as to overcome any hardware prefetching.

The achieved aggregate memory bandwidth is shown in Fig. 1(a) for several cases: when using a single chip, two chips, or all four chips in a node. Note that a BG/Q node contains only one chip whereas both the Cray XE6 and the InfiniBand cluster contain four chips – two sockets of a dualchip module of Magny-Cours and Interlagos respectively. Also note that the number of cores per chip used was varied up to the maximum on each processor chip. The maximum bandwidth observed for a single chip was 9.6 GB/s, 11.1 GB/s and 27.8 GB/s for the Magny-Cours, Interlagos, and BG/Q respectively. The same data is presented in Fig. 1(b) but in terms of memory bandwidth per-core.

It can be seen that the aggregate bandwidth generally increases with the core-count but achieves a maximum when using fewer cores than the maximum available. The per-core bandwidth, Fig. 1(b) decreases substantially on both the Magny-Cours and Interlagos processors as more cores are used, whereas on the BG/Q consistent performance is seen up to 6 cores before it degrades to 43% of its peak. It can be seen that the per-core bandwidth is comparable across all processors when using all cores in a chip.

![](_page_2_Figure_22.png)

The memory latency benchmark measures an access to main memory at 137, 170, and 400 cycles for the Magny-Cours, Interlagos, and BG/Q respectively. Note that BG/Q can also support four hardware threads per processor core (total 64 per chip) that can help improve the performance of memory latency sensitive applications.

### B. *Operating System Noise*

We examined the impact of the OS on each core using the Performance and Architecture Lab's computational noise benchmark, P-SNAP 1 . This uses a fixed-work-quantum approach in which a single computation with known expected run-time (e.g. 1ms) is repeatedly measured. The computation is measured for several million iterations and the actual time taken to complete each is recorded.

The observations were found to be highly consistent within each system, with an average slow-down of 3.5% and 0.13% per node on the InfiniBand cluster and the Cray XE6 respectively. Note that the slowdown on BG/Q was virtually zero. This reflects the approach taken on BG/Q in which the 17th core clearly achieves one of its main goals – that of offloading OS activities so that the 16 application cores progress without interruption.

## C. *Communication Performance*

The unidirectional MPI point-to-point performance is shown in Fig. 2 between a pair of processors on adjacent nodes in each system. The time for the message transfer is shown in Fig. 2(a) and bandwidth is shown in Figure 2(b). The small message latency is 1.3μs, 2.8μs, 1.8μs and the large message bandwidth is 3.6 GB/s, 1.8 GB/s, 2.8 GB/s on the Cray XE6, BG/Q and InfiniBand cluster respectively. Note that nodes that are adjacent on the E dimension on BG/Q (node 0 and 1 in this case) can use both the +/- E communication channels and hence achieve double bandwidth compared to communication with all other nodes.

The MPI point-to-point performance was also measured from core 0 in the first allocated node to core 0 in each of the other nodes. Two cases were considered: a 0-byte message representing small message latency, and a 1M-byte message representing large message bandwidth. A total of 128 nodes were used on each system. Fig. 3 shows the results from both BG/Q and the InfiniBand cluster, and Fig. 4 shows results from the Cray XE6.

The 0-byte latency on both BG/Q and the InfiniBand cluster clearly exposes the system topology. On the InfiniBand cluster, the first 12 nodes were connected to the same crossbar (with latency of 1.9μs) with the remaining 116 being on other crossbars (a further 2-hops away).

![](_page_3_Figure_8.png)

1 P-SNAP v1.2. available from http://www.c3.lanl.gov/pal/software

![](_page_3_Figure_10.png)

![](_page_3_Figure_11.png)

Figure 4. Unidirectional performance from node 0 (Cray XE6)

On BG/Q the min. latency is 2.6μs and the max. is 2.9μs. The shape of BG/Q's curve in Fig. 4(a) is pronounced and due to its 5-D network and not to any variability in the runs. The per-hop latency was observed to be ~35ns. The bandwidth observed for 1MB messages on BG/Q and the InfiniBand Cluster, Fig. 4(b), are highly consistent between nodes with very little variability. In contrast, high variability is observed for both cases on the Cray XE6. Though a min. latency between nodes of 1.6μs is observed, the typical latency is over 2.5μs and the max. observed is 6μs. Similarly the bandwidth varies between 2.2GB/s and 4.0GB/s though interestingly the observations show some repeatability across the different allocations that were scheduled. This is coincidental and the waveform seen is due in part to the tendency of scheduling together nodes that are attached to the same Gemini switch. But the main aspect observed, that of very different bandwidth and latency between nodes, with potentially high variability can clearly be seen.

#### D. *Collectives*

The performance of both MPI_barrier and MPI_allreduce (1-word) was measured using all cores on 128 nodes of the

![](_page_4_Figure_0.png)

Cray XE6 and the InfiniBand cluster, and 512 nodes on BG/Q. The results are shown in Fig. 5 and show very different performance between the three systems. Note the use of a log scale. There is some variability on the Cray XE6 and the InfiniBand cluster, but virtually none on BG/Q. The collectives on Cray are an order of magnitude faster than on the Qlogic InfiniBand network. The collectives on BG/Q are an order of magnitude faster than the Cray collectives on large core-counts even though there is no longer a dedicated collective network this latest Blue Gene.

#### E. *Communication Patterns*

The *shift* communication pattern was used to analyze the performance of each network. In this pattern each processor Pisends a message to *Pi+d* for all processor-cores i and for a logical shift distance d. This is measured for a range of distances, *d=1..n* where n is the number of processes. A different communication pattern occurs for each distance. Such patterns closely correspond to those that occur in regular dense grid applications when exchanging boundary data between sub-grids. They also approximate to the communication patterns in many irregular-grid applications. The bandwidth observed for a distance of up to 127 is shown in Fig. 6 when using 128 nodes of each system.

Negligible variability was observed on BG/Q and only a small amount on the InfinBand cluster even when using different allocations. The bandwidth varied from 600 MB/s

![](_page_4_Figure_5.png)

to 2 GB/s on BG/Q and reflects different contention within the 5-D torus for the different communication patterns. On the InfiniBand cluster, the bandwidth varied between 1.3 GB/s and 2.5 GB/s. This also reflects contention within the network by at most a factor of two and is due in the most part to the static routing employed in the Qlogic switch [15].

In contrast high variability is observed on the Cray XE6 between runs. The difference in observed bandwidth in many cases is a factor of three, and results from both differences caused by the shift pattern and its resulting network use when using different allocations as well as inter-job interference in the network. These effects are inherent in the production operation of the Cray XE6 systems.

#### V. APPLICATION PERFORMANCE

Four applications were used to compare and contrast the BG/Q, Cray XE6, and InfiniBand systems. An overview of DNS3D, MiLC, GTC, and Nek-Bone is provided below. These applications were selected due to their high use of several current leading-class supercomputing systems.

Application performance is measured in a weak-scaling mode in which the per-core sub-domain size remains fixed and the global problem increases with core-count. All the tests, were measured using five different allocations and five runs on each allocation on each system. Where appropriate the mean of the measurements is shown as well as their range (minimum and maximum).

#### 1) *Gyro-kinetic Toroidal Code (GTC)*

The Gyro-kinetic Toroidal Code (GTC) [16] is a 3D particle-in-cell code developed by the Princeton Plasma Physics Laboratory to study micro-turbulence in magnetically confined fusion plasmas. At small scales, the global tokamak domain used in GTC is partitioned along the one-dimensional toroidal dimension; at larger scales the domain is additionally partitioned in the orthogonal dimension. For the weak-scaling runs, the number of particles of each species (ions and electrons) was set to 3.2 M per core. Communication patterns at all scales consist primarily of one-dimensional nearest-neighbor messages whose sizes vary with the sub-domain size. Typical sizes are between 250 KB and 850 KB.

#### 2) *Direct Numerical Simulation (DNS3D)*

Direct Numerical Simulation (DNS) is a powerful approach that allows exact calculation of the disorderly nonlinear fluctuations that occur over time. DNS3D is a specific DNS code developed by Sandia and Los Alamos National Laboratories [17]. It employs a four-stage Runge-Kutta stepping scheme to numerically integrate the Navier-Stokes equations in the spectral space [18]. It uses heavily Fast Fourier Transforms (FFTs) with each step consisting of three 3D FFTs and six inverse 3D FFTs as well as other local computation. The 3D FFTs are implemented as a sequence of 1D FFTs computed locally followed by inter-processor transposes. For the weak-scaling runs, a total of 1283 gridpoints were assigned to each processor-core.

## 3) *MIMD Lattice QCD (MILC)*

The MIMD Lattice QCD Computation (MiLC) [19] is used to address fundamental questions in high-energy and nuclear physics including the study of the strong interactions of subatomic particles and their behavior under extreme conditions. A CG solver dominates MiLC's runtime, though memory access is a bottleneck for many systems. When using a sub-grid size of 6x4x4x3 in a weak-scaling mode, only tens of microseconds are required for each CG iteration and two small payload global reductions. Therefore, performance is very sensitive to collectives and to OS noise. Additional communications consists of stencil boundary exchanges in four dimensions. For the problem studied, payload sizes are less than 10KB, and several messages are exchanged between neighbors in each CG iteration.

#### 4) *Incompressible Fluid Flow Kernel (Nek-Bone)*

Nek5000 is an incompressible fluid flow solver used to study turbulent flows within the cores of modern nuclear reactor designs. It has been recognized with a Gordon Bell prize [20] and is one of the leading applications that will utilize the MIRA Blue Gene/Q system at Argonne National Laboratory. A kernel of Nek5000 code representing the Conjugate Gradient (CG) solver is contained within the Nek-Bone mini application. Nek-Bone uses a 3-D grid defined by the spectral element order, and the number of elements per core – set at 10 and 8 respectively here. The grid is partitioned in all three dimensions so as to minimize communication traffic between processor-cores. Boundary exchanges take place during each iteration of the CG-solver as well as two global reduction collectives. The message sizes of the boundary exchanges varied between 8 and 4KB.

### B. *Scaling Performance*

To examine performance when scaling to large core counts, we executed each application in a weak-scaling mode (i.e., fixed problem size per processor core). Results are shown in Fig. 7 for each of the four applications. In the case of the Cray XE6, the average iteration time is plotted along with the minimum and maximum times observed. Application performance on the Cray Gemini 3D torus network can be seen to be sensitive to node allocation, both in terms of the logical task to physical resource mapping within the allocation as well as to interference caused by concurrently execution jobs sharing physical network links.

At small scale, overall application performance is largely determined by single-core and single-socket performance, giving the performance advantage to the InfiniBand and XE6 systems. However, at larger scales the superior scaling characteristics of the BG/Q system become apparent. Most noticeably, a crossover point is reached in which BG/Q outperforms the InfiniBand cluster on a given problem size and processor core count. For three of the applications, this crossover point is at a small scale (less than 1,000 cores).

The worst observed scaling performance belongs to the InfiniBand cluster. In some cases, this has as much to do with the fact that the InfiniBand cluster contains the largest number of processor cores per node, increasing the communication pressure at the network endpoints and the contention observed in the network. However, in the case of Nek-Bone and MiLC, performance is determined by that of a conjugate gradient (CG) solver making application performance sensitive to MPI collective performance and Operating System noise. As observed in Section IV(D),

![](_page_5_Figure_7.png)

Figure 7. Application performance scaling across systems (weak-scaling).

collective performance suffers on the InfiniBand cluster. Combined with a heavy-weight OS kernel executing on each processor core, this leads to variable performance and overall application performance degradation.

#### VI. ANALYSIS OF RESULTS

In this section we consider two types of analysis. The first provides a look on how much slower (or faster) Blue Gene/Q performs against the Cray XE6 and InfiniBand cluster on an equal node basis. This takes into account the differences between nodes that are not seen in comparing the performance on an equal core-count basis. The second quantifies how much application performance is being lost due to the way in which the systems are both configured, and in particular how nodes are allocated on each system.

## A. *Relative performance*

There are many possible bases for a comparison across systems including: core-count, node-count, network endpoints, memory controllers, memory capacity, and memory bandwidth, to name a few. Each will bias the comparison in different ways. We base the relative performance between the systems on equal node counts. The performance per node is calculated as the amount of work undertaken on all cores in a node whose core-count varies across the three systems.

The relative performance between BG/Q, the Cray XE6 and InfiniBand cluster is shown in Fig. 8 for the four applications using up to 256 nodes. Note that a relative performance greater than one means that the machine outperforms BG/Q by that factor, and a relative performance below unity means BG/Q is faster.

It is clear that both the Cray XE6 and InfiniBand cluster outperform BG/Q at low node counts and that all four applications scale better on BG/Q, hence relative performance decreases with node count. As seen earlier in Fig. 7, there are clear scales at which BG/Q exceeds the performance of the Cray and InfiniBand systems. For three out of the four applications, BG/Q is seen to match or exceed the performance of the InfiniBand cluster within the range of

![](_page_6_Figure_0.png)

![](_page_6_Figure_1.png)

- 

Figure 8. Performance of Cray XE6 and InfinBand relative to BG/Q nodes used. This is due to higher noise on the InfiniBand

cluster for MiLC and Nek-Bone, and due to the lower

There are several effects that can be seen in Fig. 9. In particular, we see that BG/Q has very little lost performance with predictions matching observations almost exactly. This is due to i) having a 17th core to assist in support activities and hence eliminate OS-noise, ii) preserving job isolation in the way in which nodes are allocated, and *iii)* use of a high a dimensional mesh that reduces intra-job contention effects – though these should become more apparent on larger systems, our test system had at most a 4x4x4x4x2 5-D torus. The performance lost on both the Cray XE6 and

network bandwidth that impacts the all-to-all collective operations for DNS3D. BG/Q also achieves higher performance for DNS3D than the Cray XE6 when using 256 nodes or more. This is again due in the main part to the higher injection bandwidth into the 5-D torus on BG/Q than the XE6. The Cray XE6 achieves higher performance than BG/Q on the other three applications though its relative performance decreases with scale.

## B. *Lost Performance*

To analyze the possible performance lost due to the systems' node allocation methods, we employ a set of previously developed and validated performance models, one for each application. Our models for DNS3D and MiLC were initially developed for performance analysis of Blue Waters [21], the model for GTC was initially developed for analyzing the performance of the Cray XT4/XT5 [22], and the model for Nek-Bone was recently developed for use within the DOE CESAR co-design center [23]. The models are used to predict the best performance that each application should achieve, given the performance characteristics of each system, including injection bandwidth, network link bandwidth, network latency, network topology and routing, collective performance, as well as application performance on a node when using all cores and a given OS-noise profile. These factors were presented in Section IV for each system.

The difference between the best expected performance and observed performance includes a number of factors – in particular it includes the performance lost to operating system effects, from non optimal task-to-core mapping (due to the ways in which nodes are allocated in a system as discussed in Section III), and due to interaction between jobs sharing resources such causing contention on the network in the Cray XE6. The lost performance is shown in Fig. 9 for each the application on each system. This is taken as the difference between the best performance as predicted, and the average observed performance.

InfiniBand cluster generally increases with node count. On the Cray XE6 it is greatly influenced by the actual nodes allocated in the tests performed and impacts intra-node contention as well as causing the variability across tests noted in Section VI. The InfiniBand cluster is more subject to the lower than ideal bandwidth in the network, seen in Fig. 6(a), due to static routing that causes contention in the network, and to high OS noise.

## VII. RELATED WORK

This work is a first performance comparison of Blue Gene/Q against current leading HPC systems that uses micro-benchmarks and production applications. In addition, performance models were used to quantify the difference between that each system is capable of in the best case and that observed in production use. As far as the authors are aware there is currently no published analysis of Blue Gene/Q other than detailed descriptions of its architecture and its peak capabilities. This includes details on the Blue Gene/Q processor [4], and it's interconnection network [2,3].

Microbenchmarks for analyzing the performance of networks are widespread especially in terms of point-to-point messaging and collective communication. Such analysis is often coupled with application performance under varying configurations but often lacks modeling or simulation that assists in relating individual aspects of the architecture to the observed application performance. Recent representative work on the empirical analysis of large-scale systems includes that for clusters using Intel processors [24], Cray XE6 systems [22], and comparisons across systems [8,26].

There are a number of other works that use modeling approaches similar to our own including that in use for the exploration of extreme scale systems e.g. [27]. Many of these approaches are often limited in their predictive accuracy, and have not been through an extensive validation process on current systems. In addition a number of simulators are in development, e.g. [28,29] that promise high accuracy for large-scale systems but often require high runtime or large resources to provide predictions.

#### VIII. CONCLUSIONS

In this work we have provided a first performance analysis of Blue Gene/Q that uses both micro-benchmarks and a set of production applications. In particular we compare its performance with two other leading HPC systems, namely the Cray XE6 and an InfiniBand cluster. The analysis of sub-system performance shows that each processor-core of BG/Q achieves a similar memory bandwidth as to the AMD processors used in the other machines. It has shown that OS noise is virtually eliminated from the use from the 17th (non-application core). In addition, inter-node communication on the 5-D torus allows for almost 1.8GB/s in each direction from the processor, and that the collective performance also scales extremely well.

Applications achieved better scalability on BG/Q than on the Cray XE6 and the InfiniBand cluster. This, given its modest per-core and per-node performance, also resulted with BG/Q achieving higher application performance in many cases within the node range used in this analysis. This bodes well for the performance of large-scale BG/Q systems.

This work illustrates some of the issues associated with node allocation on especially on the Cray XE6 systems that causes both variability and lost performance due to inter-job interference as well as non-optimal mapping of the application onto the allocated nodes. This contrasts with the approach of Blue Gene in which the topology of nodes is known in advance and which is isolated from other jobs when shared resources (e.g. file-system) are not used.

#### ACKNOWLEGEMENTS

The Pacific Northwest National Laboratory is operated by Battelle for the U.S. Department of Energy under contract DE-AC05-76RL01830.

#### REFERENCES

- [1] R. Alverson, D. Roweth, and L. Kaplan, "The Gemini System Interconnect," Proc. 18th IEEE Symp. on High Performance Interconnects, pp. 83-87, 2010.
- [2] D. Chen, N.A. Eisley, P. Heidelberger et. al., "The IBM Blue Gene/Q Interconnection Network and Message Unit," Proc. IEEE/ACM Supercomputing (SC'11), Seattle, WA, 2011.
- [3] D. Chen, N.A. Eisley, P. Heidelberger, et. al., "The IBM Blue Gene/Q Interconnection Fabric," IEEE Micro, 32(1), 2012, pp. 32-43.
- [4] R.A. Haring, M. Ohmachtm T.W. Fox et. al., "The IBM Blue Gene/Q Compute Chip," IEEE Micro, 32(2), 2012, pp. 48-60.
- [5] http://www.mellanox.com/
- [6] R. Brightwell, K. Pedretti, and K.D. Underwood, "Initial Performance Evaluation of the Cray SeaStar Interconnect," Proc. 13th Symp. on High Performance Interconnects (HOTI'05), 2005.
- [7] J. Kim, W.J. Dally, S. Scott, and D. Abts, "Cost-Efficient Dragonfly Topology for Large-Scale Systems," IEEE Micro 29(1), 2009, 33-40.

- [8] A. Hoisie, G. Johnson, D.J. Kerbyson, M. Lang, and S. Pakin, "A Performance Comparison through Benchmarking and Modeling of Three Leading Supercomputers: Blue Gene/L, Red Storm, and Purple," Proc. IEEE/ACM Supercomputing (SC'06), Tampa, 2006.
- [9] http://www.nersc.gov/users/computational-systems/hopper/
- [10] http://pic.pnnl.gov/
- [11] A. Bhatele, and L.V. Kale, "Benefits of Topology-aware Mapping for Mesh Topologies," Parallel Processing Letters, 18(4), 2008, pp. 549- 566.
- [12] E. Zahavi, G. Johnson, D.J. Kerbyson, and M. Lang, "Optimized Infiniband Fat-tree Routing for Shift All-to-All Communication Patterns," Concurrency And Computation: Practice and Experience, 22(20), 2010, pp. 217-231.
- [13] F. Petrini, D.J. Kerbyson, and S. Pakin, "The Case of the Missing Supercomputer Performance: Achieving Optimal Performance on the 8,192 Processors of ASCI Q," Proc. IEEE/ACM Supercomputing (SC'03), Phoenix, AZ, 2003.
- [14] J. McCalpin, "Memory bandwidth and machine balance in current high performance computers," in IEEE Comp. Soc. Tech. committee on Computer Architecture (TCCA) Newsletter, 1995, pp. 19-25.
- [15] D.J. Kerbyson, M. Lang, and G. Johnson, "Infiniband Routing Table Optimizations for Scientific Applications," Parallel Processing Letters, World Scientific Publishing, 18(4), 2008, pp. 589-608.
- [16] S. Ethier, W.M. Tang, and Z. Lin, "Gyrokinetic Particle-in-cell Simulations of Plasma," Microturbulence on Advanced Computing Platforms, Journal of Physics: Conference, Series 16 2005, pp. 1-15
- [17] S. Kurien, and M. Taylor, "Direct Numerical Simulation of Turbulence: Data Generation and Statistical Analysis," Los Alamos Science, Vol 29, 2005, pp. 142-151.
- [18] D.A. Donzis, P.K. Yeung, and D. Pekurovsky, "Turbulence simulations on O(104 ) processors," in *Proc. TeraGrid*, 2008.
- [19] Bernard C., Et. al., "Studying Quarks and Gluons on MIMD Parallel Computers," Int. J. of Supercomputing Applications, 1991, 5(16).
- [20] H.M Tofo, and P.F. Fischer, "Terascale Spectral Element Algorithms and Implementations," Proc. IEEE/ACM Supercomputing (SC'99), Portland, OR, 1999.
- [21] D.J. Kerbyson, and K.J. Barker, "A Performance Model of Direct Numerical Simulation for Analyzing Large-Scale Systems," Proc. Workshop on Large-Scale Parallel Processing (LSPP), Int. Parallel and Distributed Processing Symposium (IPDPS), Anchorage, 2011.
- [22] K. Davis, K.J. Barker, and D.J. Kerbyson, "Performance Prediction Via Modeling: A Case Study of the ORNL Cray XT4 Upgrade," Parallel Processing Letters, World Scientific Publishing, 19(4), 2009.
- [23] http://cesar.msc.anl.gov/
- [24] S. Saini, A. Naraikin, R. Biswas, D. Barkai, and T. Sandstrom, "Early Performance Evaluation of a Nehalem Cluster Using Scientific and Engineering Applications," Proc. IEEE/ACM Supercomputing (SC'09), Portland, OR, 2009.
- [25] C. Vaughan, M. Rajan, R.F. Barrett, D. Doerfler, and K.T. Pedretti, "Investigating the Impact of the Cielo Cray XE6 Architecture on Scientific Application Codes," Proc. Workshop on Large-Scale Parallel Processing (LSPP), Int. Parallel and Distributed Processing Symposium (IPDPS), Anchorage, May 2011.
- [26] A. Bhatele, L. Wesolowski, E. Bohm, E. Solomonik and L.V. Kale, "Understanding application performance via micro-benchmarks on three large supercomputers: Intrepid, Ranger and Jaguar," Int. J. of High Performance Computing Applications (IJHPCA), 2010.
- [27] A. Bhatele, P. Jetley, H. Gahvari, L. Wesolowski, W.D. Gropp, and L.V. Kale, "Architectural Constraints Required to Attain 1 Exaflop/s for Scientific Applications," in Proc. Int. Parallel and Distributed Processing Symposium (IPDPS), Anchorage, 2011.
- [28] Rodrigues, R.F., et.al, 2011. The Structural Simulation Toolkit, ACM Sigmetrics Performance Evaluation Review, 38(4), pp. 37-42.
- [29] G. Zheng, G. Kakulapati, and L.V. Kale. "BigSim: A Parallel Simulator for Performance Prediction of Extremely Large Machines," Proc. Int. Parallel and Distributed Processing Symposium (IPDPS), Santa Fe, 2004.

