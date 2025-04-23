# Towards the Automated Generation of Hard Disk Models Through Physical Geometry Discovery

S. A. Wright, S. J. Pennycook, S. A. Jarvis

Performance Computing and Visualisation Department of Computer Science University of Warwick, UK Email: steven.wright@warwick.ac.uk

*Abstract*—As the High Performance Computing industry moves towards the exascale era of computing, parallel scientific and engineering applications are becoming increasingly complex. The use of simulation allows us to predict how an application's performance will change with the adoption of new hardware or software, helping to inform procurement decisions.

In this paper, we present a disk simulator designed to predict the performance of read and write operations to a single hard disk drive (HDD). Our simulator uses a geometry discovery benchmark (Diskovery) in order to estimate the data layout of the HDD, as well as the time spent moving the read/write head. We validate our simulator against two different HDDs, using a benchmark designed to simulate common disk read and write patterns, demonstrating accuracy to within 5% of the observed I/O time for sequential operations, and to within 10% of the observed time for seek-heavy workloads.

*Keywords*-Data Storage Systems, File Systems, High Performance Computing, I/O, Simulation

## I. INTRODUCTION

The High Performance Computing (HPC) industry is aiming to deliver exascale computing before 2020. As we move towards this goal, the diverse choice of hardware and software available has made the task of choosing the most appropriate platform increasingly difficult for HPC centres worldwide. The use of many-core architectures has boosted the floatingpoint arithmetic performance (FLOP/s) of supercomputers beyond the petaflop barrier, but many of the contributory components of these systems have not witnessed the same level of development. Many of these components are now seen as potential bottlenecks to applications being run at exascale.

In addition to the wide variety of parallel processing solutions available, storage systems have also become increasingly varied. The high performance storage systems connected to today's supercomputers can be separated into two categories: (i) specialised hardware and software, from companies such as EMC or Panasas; and (ii) commodity hardware, backed by proprietary parallel file systems such as IBM's General Parallel File System (GPFS) or open-source alternatives like Lustre and the Parallel Virtual File System (PVFS). The task facing many HPC centres is now deciding not only which hardware to invest in to increase compute performance, but also which I/O subsystem is best suited for their applications.

To aid in procurement decisions, modelling and simulation techniques are being increasingly employed. Through simulation, a hypothetical machine can be benchmarked in order to predict how a real architecture may perform, informing the procurement process.

In this paper we propose a new disk simulator, designed to simulate the mechanical behaviour of a spinning hard disk drive (HDD). Although much of the physical layout of data on a disk is hidden from the end-user (and indeed the computer and operating system to which it is connected), we are able to approximate much of this information using a novel benchmark.

Specifically, the contributions of this paper are the following:

- We describe the design and implementation of a hard disk benchmarking tool named Diskovery, designed to predict the bit-layout of a HDD, accounting for the use of Zoned-Bit Recording (ZBR);
- Using the information gathered, we generate a simple physical disk model that estimates timing information for read, write and seek operations on the disk;
- Finally, we validate our disk model against two retail HDDs from Maxtor and Seagate, using a benchmark designed to test both random and sequential access patterns. Our generated model demonstrates a high degree of accuracy, predicting performance to within 5% of observed timings for sequential operations, and to within 10% of observed timings for seek-heavy workloads.

The remainder of this paper is structured as follows: Section II summarises previous research in disk and file system simulation; Section III outlines how we characterise the performance of a HDD; Section IV explains the construction of our disk model from the performance metrics discovered previously; Section V demonstrates the performance of our disk model against two distinct HDDs; Section VI concludes this paper, presenting direction for future research.

## II. RELATED WORK

Performance modelling and simulation have been previously used to predict the compute performance of various science codes at varying scales on hypothetical supercomputers. Analytical models (predominantly based on the LogGP [1] model) have been heavily used to analyse the scaling behaviour of hydrodynamic [2] and wavefront codes [3], as well as many other classes of applications [4], [5]. Similarly, simulation based models have been heavily utilised where network contention makes analytical modelling difficult [6], [7].

Two such simulation platforms have been developed recently at Sandia National Laboratories and the University of Warwick. The Structural Simulation Toolkit (SST) [8], from Sandia, provides a framework for both macro-level and micro-level simulation of parallel science applications, simulating codes at an abstract level (predicting MPI behaviours and approximate function timings), as well as at a microinstruction level. Similarly, the Warwick Performance Prediction (WARPP) [9] toolkit simulates parallel science codes at macro-level, and includes simulation parameters to introduce network contention (through the use of a Gaussian distribution of background load).

While SST includes an optional plugin to simulate hard disk performance (using DiskSim [10]), the module is not included by default and is currently not capable of simulating a parallel file system. Furthermore, compilation of DiskSim is complicated by its lack of development since 64-bit architectures became commonplace. Simulation of a HDD using DiskSim relies on the target disk being benchmarked using the DIXtrac [11] application, which determines the values for "over 100 performance-critical parameters", including some of the parameters we utilise in this work. However, the model generated by DIXtrac for use with DiskSim is complex, and can take a substantial amount of time and processing power to generate usable results. Conversely, we use a small subset of these parameters to model only the physical aspects of the HDD, simplifying our model and thus improving the time-to-prediction.

Additional work into disk simulation has been done by both IBM and Hewlett-Packard (HP) Laboratories. In [12], the authors use a trace driven simulation to analyse the performance gains of various I/O optimisations and disk improvements. They assess the benefits of read caching, prefetching and write buffering, demonstrating their benefits to improving I/O performance. Likewise, Ruemmler and Wilkes [13] assess the benefit of disk caching using a simulation, demonstrating a large error in predictions for small operations when the cache is not modelled, highlighting the importance of disk cache modelling.

Early disk caches (typically less than 2 MB in size) would partition their available storage into equally sized blocks to allow multiple simultaneous read operations to utilise the cache. Modern hard disks do not have this same restriction, instead partitioning the cache according to some heuristic. In [14], they demonstrate, using a simulator, that the disk's cache hit-ratio can be improved by using an online algorithm to dynamically partition the cache. Similarly, Zhu and Hu [15] demonstrate the benefit of both read caching and write caching on sequential workloads, but conclude that there is very little benefit when there are more concurrent workloads than cache segments. Currently we concentrate only on the physical aspects of a HDD; we leave I/O controller optimisations to future work.

In order to incorporate our disk model into a simulation toolkit (such as SST), it will not only be required to simulate a single disk, but also RAID configurations [16], and parallel file systems [17]–[19]. In [20], the authors build a "scaffold" interface in order to allow them to use a real file system module to simulate performance. Their scaffolding simulator mimics many of the operations that would otherwise be performed by the kernel in order to bypass writing to physical media, instead directing data towards a disk model.

Simulating parallel file systems is a much more difficult task, instead requiring the simulation of both a shared metadata target, as well as multiple data targets. Molina-Estolano *et al.* have developed IMPIOUS [21], a tracedriven parallel file system simulator that attempts to mimic a storage system using PanFS [19]. Interestingly, although their results are out by an order of magnitude, the linear trend of their results is similar to the true performance.

Both [22] and [23] utilise the CODES storage system simulator to predict the performance of a large PVFS installation at the Argonne National Laboratory. In [22] they use their model to predict the benefit of burst-buffer solid state drives (SSD) within their installation, concluding that performance may be greatly improved if burst buffer disks were deployed more readily.

Finally, in [24], Carns *et al.* utilise a simulator of PVFS in order to demonstrate the inefficiencies in server-to-server communication, used to maintain file consistency. They modify the algorithms used by PVFS and demonstrate speedups in file creation, file removal and file stat operations. The application of a simulation to performing these types of optimisations is one of the main motivations for this work.

In this paper we report on the initial development of our own simulator, the Distributed File System Simulator (DFSsim). The eventual goal of this work is to simulate a full Lustre file system within the SST framework; this paper outlines our current progress in simulating the physical aspects of a HDD. In future work we intend to model the caching and queuing effects, used in all modern SATA hard drives, as well as modelling both standard UNIX file systems (*e.g.* XFS, ext3) and parallel file systems (*e.g.* Lustre, GPFS).

![](_page_2_Figure_0.png)

Figure 1. Time taken to read 200 MB of sequential data from (a) the M250, and (b) the S320.

## III. DISK DRIVE CHARACTERISATION

## *A. Disk Drive Performance*

Characterising the performance of a spinning HDD is a very difficult task, with a wide variety of metrics that may be relevant. Manufacturers will often quote the bus type and bandwidth (*e.g.* SATA-II, 3 Gbit/s), in addition to the size of the disk cache, as the most important performance metrics. The maximum "burst" data rate (typically the same as the bus bandwidth) and sustained data rate will also often be quoted in manufacturer data sheets. The performance of a HDD in a typical system is often very different, complicated by the use of complex data layout schemes and caching policies.

In a typical modern HDD, sequential read and write performance varies depending on the location of the data on the disk platters. When data is written to the innermost tracks of the disk there are many less available data blocks in the physical space, and therefore, the data is written at a slower rate (since the rotation speed is usually fixed).

Whilst maximum utilisation of the disk's surface could be achieved by maintaining the maximum block density for every track, this is not practical due to the overhead of managing data positioning, as well as the maximum speed at which the read/write head can operate on the outer tracks. For this reason the surfaces are subdivided into zones of a fixed density and width; this is known as ZBR. This approach strikes a balance between maximising the usage of the disk's surface, and simplifying the operation of the disk's onboard controller for data layout. However, this introduces variability in the maximum achievable bandwidth from each zone. Modern HDDs use between 10 and 30 zones, although the exact number of zones and their dimensions (width and density) for a particular model is not usually made public.

As well as the data layout dictating the disk's performance, the rotational latency and the head seek time are major contributors to disk performance. Most workstations use 7,200 RPM disks, and therefore perform 120 complete revolutions per second. To locate a random data segment on the disk requires, on average, half a rotation of the platters and therefore will take approximately 4.17 ms. Seeking to a particular track on the disk requires the read/write head to accelerate towards its maximum speed, coast for a period, before decelerating to a stop. The head must then "settle" before data is written or read. The average seek time of modern hard disks is usually about 8.0-9.0 ms, but will be considerably longer for a full stroke (from the innermost track to the outermost track, or vice versa) and significantly smaller for a track-to-track seek (typically taking between 0.2 and 0.8 ms).

Predicting the performance of HDDs is further complicated by the disk cache. With the decreasing cost of fast random access memory, manufacturers are increasing disk cache sizes in order to improve the burst bandwidth of their HDDs, with drives typically utilising between 4 and 32 MB of disk cache. Read-ahead caching is utilised in order to artificially boost the burst read speed (by reading ahead a number of blocks whilst the disk is otherwise idle), but sustained bandwidth is affected very little by the use of a disk cache. Write-back caching is also used to boost write performance, where small writes are performed to the cache and only committed to the disk's platters at a later time, when the cache space is needed.

The use of Tagged Command Queuing, and more recently Native Command Queuing (NCQ) on SATA HDDs, has further improved the performance of disk drives. The operating system can queue up a series of read or write requests and the disk can then reorder these requests in order to serve them in the most appropriate order (for instance, performing a small read during a seek to another section of the disk).

## *B. Disk Drive Characterisation*

In this paper we present Diskovery, a purpose-built benchmark designed to: (i) estimate the densities and widths of a

![](_page_3_Figure_0.png)

Figure 2. Seek time plotted against seek distance for: (a) and (b), the M250; and (c) and (d), the S320.

Table I SPECIFICATION OF THE DISKS USED IN THIS STUDY.

|  | M250 | S320 |
| --- | --- | --- |
| Manufacturer | Maxtor | Seagate |
| Model Number | 7Y250M0 | ST3320418AS |
| Size (GB) | 250 | 320 |
| Surfaces | 6 | 2 |
| Spindle Speed (RPM) | 7,200 | 7,200 |
| Bus Connection | SATA-I 1.5 Gbit/sec | SATA-II 3 Gbit/sec |

hard disk's zones; and (ii) characterise a drive's seek time as a series of equations. We study two disks, summarised in Table I.

The results in this paper were all generated after disabling read and write caching (using hdparm), as well as reducing the queue size to 1 (effectively disabling NCQ). Whilst this decreases the performance of the disk drive, it allows for more accurate detection of the geometry of the HDD. We leave the discovery of extra drive parameters, such as cache size and NCQ size, to future work.

Diskovery first attempts to estimate the number of zones used by a disk. This is achieved by reading or writing a fixed amount of data at increasing offsets. We read 200 MB of data in 4 MB blocks, in order to ensure that no caching effects are present. Figure 1 shows the time taken to read 200 MB of data from each of the disks, with the cache disabled. Using a simple step detection algorithm (where a new step is defined as a difference in execution time of more than 2 standard deviations from the current step mean), we estimate that both disks have 16 distinct zones (as can be seen by the stepping effect in Figures 1(a) and (b)). Although our benchmark could refine the point at which each zone starts and ends, we instead use the midpoint as an approximation, since we do not believe it will greatly affect our model's predictions. Given the spindle speed (7,200 RPM for both of the HDDs used in this study), we can estimate the number of 512-byte blocks read per complete rotation, and thus the density of any given zone. The zone widths can be estimated using the approximate start and end offset of each zone (as zone width × zone density = zone block size).

TIME TAKEN (IN SECONDS) TO PERFORM 1,000 SEQUENTIAL OPERATIONS AT AN OFFSET OF: (a)–(b), 0 GB; AND (c)–(d), 200 GB.

|  |  | Read |  |  | Write |  |  |  | Read |  |  | Write |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Block | Observed | Predicted | Error | Observed | Predicted | Error | Block | Observed | Predicted | Error | Observed | Predicted | Error |
| 1 | 8.54 | 8.35 | 2.23% | 8.55 | 8.35 | 2.36% | 1 | 8.55 | 8.35 | 2.41% | 8.56 | 8.35 | 2.50% |
| 2 | 8.54 | 8.37 | 2.01% | 8.56 | 8.37 | 2.21% | 2 | 8.56 | 8.36 | 2.29% | 8.58 | 8.36 | 2.51% |
| 4 | 8.55 | 8.40 | 1.69% | 8.58 | 8.40 | 2.02% | 4 | 8.57 | 8.39 | 2.12% | 8.58 | 8.39 | 2.21% |
| 8 | 8.56 | 8.47 | 1.03% | 8.62 | 8.47 | 1.67% | 8 | 8.56 | 8.44 | 1.38% | 8.57 | 8.44 | 1.49% |
| 16 | 8.62 | 8.62 | 0.06% | 8.67 | 8.62 | 0.66% | 16 | 8.56 | 8.55 | 0.12% | 8.58 | 8.55 | 0.30% |
| 32 | 8.73 | 8.90 | 1.97% | 8.81 | 8.90 | 1.00% | 32 | 8.57 | 8.77 | 2.36% | 8.58 | 8.77 | 2.20% |
| 64 | 9.04 | 9.46 | 4.72% | 9.07 | 9.46 | 4.30% | 64 | 8.74 | 9.21 | 5.43% | 8.74 | 9.21 | 5.47% |

(a) M250

(b) S320

|  |  | Read |  |  | Write |  |  |  | Read |  |  | Write |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Block | Observed | Predicted | Error | Observed | Predicted | Error | Block | Observed | Predicted | Error | Observed | Predicted | Error |
| 1 | 8.59 | 8.36 | 2.78% | 8.62 | 8.36 | 3.03% | 1 | 8.59 | 8.35 | 2.85% | 8.59 | 8.35 | 2.84% |
| 2 | 8.61 | 8.38 | 2.65% | 8.63 | 8.38 | 2.96% | 2 | 8.61 | 8.36 | 2.87% | 8.62 | 8.36 | 2.98% |
| 4 | 8.64 | 8.42 | 2.53% | 8.66 | 8.42 | 2.75% | 4 | 8.62 | 8.39 | 2.67% | 8.63 | 8.39 | 2.70% |
| 8 | 8.68 | 8.51 | 2.01% | 8.71 | 8.51 | 2.27% | 8 | 8.65 | 8.46 | 2.24% | 8.66 | 8.46 | 2.34% |
| 16 | 8.76 | 8.69 | 0.91% | 8.80 | 8.69 | 1.36% | 16 | 8.70 | 8.58 | 1.40% | 8.71 | 8.58 | 1.49% |
| 32 | 8.97 | 9.04 | 0.74% | 9.01 | 9.04 | 0.28% | 32 | 8.79 | 8.82 | 0.35% | 8.80 | 8.82 | 0.18% |
| 64 | 9.41 | 9.74 | 3.56% | 9.41 | 9.74 | 3.49% | 64 | 8.99 | 9.31 | 3.53% | 8.99 | 9.31 | 3.59% |

(c) M250

(d) S320

Secondly, Diskovery derives a series of equations describing the seek time of a HDD. We consider seek time to be the time to move the head between two tracks plus the time taken for half a rotation of the disk's surface. Given the ZBR information discovered, Diskovery calculates approximate offsets for each track of the disk and then performs a seek between the 0th track (at offset 0), and a predetermined offset for a particular track (calculated using an additive randomised factor between −1000 and 1000 in order to average out the influence of uneven rotations). We then determine the seek time to be the average of 100 operations, minus the time to read or write a single block at the given offset and the average rotational latency.

Figure 2 shows the relationship between seek distance and seek time for both the S320 and the M250. For small seeks, head acceleration and deceleration cause a logarithmic growth in seek time; for larger seeks, the time grows linearly (as the head coasts at its maximum speed for a period).

We calculate two regression lines to model: (i) the logarithmic portion of the curve, using a power regression (*i.e.* a · x b ); and (ii) the linear portion, using a simple linear regression (*i.e.* c + dx). For (i) we use a portion of the data starting at the smallest possible seek, increasing the amount of data used until we minimise the coefficient of determination, for (ii) we use the upper portion of the data, until we again find the minimum coefficient of determination for our observed data. We then solve the simultaneous equations to find the lowest intersection between the two equations. Our final seek model can then be expressed as:

$$f(x)={\left\{\begin{array}{l l}{a\cdot x^{b}}&{{\mathrm{if~}}x<C}\\ {c+d x}&{{\mathrm{otherwise}}}\end{array}\right.}$$

Where a, b, c and d are the variables calculated for our regression lines, C is the lowest crossover point for our class IStorageDevice { public:

// return time to read count bytes at offset virtual double read(long offset, long count) = 0; // return time to write count bytes at offset virtual double write(long offset, long count) = 0; // return number of blocks on disk virtual long getBlockSize() = 0;

};

Figure 3. C++ interface used in DFSsim to represent a storage device.

equations and x is the number of tracks we wish to seek.

As demonstrated in Figure 2, the seek time can vary for read and write operations and we therefore model these separately. For the M250 (Figures 2(a) and (b)), the seek time differs significantly for read and write operations, motivating the separate modelling of these two operations. The S320 (Figures 2(c) and (d)) however, behaves relatively consistently between read and write operations.

## IV. DISK MODELLING

Our simulation framework makes use of two C++ interfaces, namely IStorageDevice and IFileSystem. In this paper we focus only on modelling the storage device itself and we leave file system simulation to later work.

As shown in Figure 3, which outlines the simple interface used to simulate a HDD in DFSsim, the IStorageDevice class contains three virtual functions that require implementation.

Using the data gathered from each of the disk drives benchmarked, we create an implementation with an array containing the zone widths and zone densities calculated previously. Our implementation also maintains last track accessed (but not the last offset). Since we do not expect the timing information for a given simulation to be within one 120th of a second, we choose not to model the exact location

| Table III |
| --- |
| TIME TAKEN (IN SECONDS) TO PERFORM 1,000 BLOCK STRIPED OPERATIONS AT AN OFFSET OF: (a)–(b), 0 GB; AND (c)–(d), 200 GB. |

|  |  | Read |  |  | Write |  |  | Read |  |  | Write |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Block | Observed | Predicted | Error | Observed | Predicted | Error | Block Observed | Predicted | Error | Observed | Predicted | Error |
| 1 | 8.55 | 8.36 | 2.23% | 8.56 | 8.35 | 2.50% | 8.56 1 | 8.36 | 2.41% | 8.56 | 8.35 | 2.53% |
| 2 | 8.55 | 8.38 | 2.06% | 8.58 | 8.37 | 2.41% | 2 8.57 | 8.37 | 2.29% | 8.58 | 8.36 | 2.52% |
| 4 | 8.56 | 8.41 | 1.76% | 8.61 | 8.40 | 2.38% | 8.57 4 | 8.40 | 2.04% | 8.59 | 8.39 | 2.36% |
| 8 | 8.57 | 8.48 | 1.00% | 8.63 | 8.47 | 1.80% | 8 8.58 | 8.45 | 1.44% | 8.62 | 8.44 | 2.10% |
| 16 | 8.64 | 8.62 | 0.24% | 8.69 | 8.62 | 0.88% | 16 8.58 | 8.56 | 0.25% | 8.70 | 8.55 | 1.67% |
| 32 | 8.81 | 8.90 | 1.09% | 8.80 | 8.90 | 1.09% | 32 8.59 | 8.78 | 2.21% | 8.85 | 8.77 | 0.85% |
| 64 | 9.12 | 9.47 | 3.82% | 9.12 | 9.46 | 3.73% | 64 8.80 | 9.22 | 4.77% | 9.10 | 9.21 | 1.21% |

|  |  | Read |  |  | Write |  |  | Read |  |  | Write |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Block | Observed | Predicted | Error | Observed | Predicted | Error | Block Observed | Predicted | Error | Observed | Predicted | Error |
| 1 | 8.60 | 8.36 | 2.78% | 8.63 | 8.36 | 3.20% | 8.61 1 | 8.36 | 2.96% | 8.62 | 8.35 | 3.18% |
| 2 | 8.62 | 8.39 | 2.73% | 8.66 | 8.38 | 3.30% | 2 8.63 | 8.37 | 3.00% | 8.66 | 8.36 | 3.40% |
| 4 | 8.64 | 8.43 | 2.41% | 8.70 | 8.42 | 3.20% | 4 8.66 | 8.40 | 2.96% | 8.69 | 8.39 | 3.42% |
| 8 | 8.70 | 8.51 | 2.10% | 8.76 | 8.51 | 2.83% | 8 8.61 | 8.46 | 1.78% | 8.71 | 8.46 | 2.91% |
| 16 | 8.84 | 8.69 | 1.64% | 8.86 | 8.69 | 2.00% | 16 8.80 | 8.58 | 2.46% | 8.80 | 8.58 | 2.58% |
| 32 | 9.07 | 9.04 | 0.24% | 9.09 | 9.04 | 0.61% | 32 8.70 | 8.83 | 1.43% | 8.98 | 8.82 | 1.82% |
| 64 | 9.37 | 9.75 | 4.01% | 9.53 | 9.74 | 2.18% | 9.17 64 | 9.32 | 1.60% | 9.17 | 9.31 | 1.56% |

(c) M250

(a) M250

(d) S320

(b) S320

of the spindle, instead assuming that all operations require either an entire rotation, or half a rotation (for a given small seek). Whilst this leaves our simulated timings possibly out by half a rotation for a single function call, over the course of an entire simulation these will average out. Further, since the disk drive reads and writes in blocks of 512 bytes, our simulation also mimics this behaviour, reading entire blocks even in the case where less than one block is requested.

## V. VALIDATION

## *A. Performance Benchmark*

In order to validate the accuracy of our physical disk model, we wrote a benchmark to measure the performance of a disk and our model for four representative I/O behaviours:

## 1) Sequential:

A number of reads or writes of the same size are performed to sequential offsets, emulating the behaviour of reading a large file.

## 2) Block Striped:

At a given offset, a block of a given size is read or written, before a block of the same size is skipped, before reading or writing again. Similar behaviour may be found in a parallel application where data is strided for each process.

## 3) Random Seek:

A number of random seeks are performed on the disk before a block of a given size is read or written. This mimics a HDD's performance on a typical multiuser server system, where the data of many users is randomly distributed across the disk.

# 4) Random Size, Random Seek:

Similar to the Random Seek tests, but the block size is randomised between 1 and a given maximum block size. This gives a better representation of a multiuser system, since users may access data blocks of different sizes.

The tests outlined above perform a set number of iterations of a given size to a block device using the O_DIRECT and O_SYNC open flags. This helps to eliminate the effects of the operating systems disk caching, in addition to the device having the onboard cache and queue disabled within the operating system. Reading and writing directly to the block device also removes the overhead of file system management and data layout, although this makes the generation of a model for an in-use disk difficult. To generate random offsets in the random seek tests, we used a 64-bit variant of the Mersenne twister pseudorandom number generator (MT19937-64 [25]). The advantage of using this algorithm, instead of the default random() function, is that the range is much larger and is therefore far more representative of a real seek-heavy workload (instead of each byte offset being a multiple of 32,768).

In order to test DFSsim, we simply replace the read and write POSIX function calls with calls to the read and write operations within our implemented IStorageDevice object. Each of these operations return the estimated time taken, which we sum and report at the end of execution.

## *B. Results*

The first two experiments replicate behaviours commonly found in parallel science applications. In the first test, our benchmark reads or writes 1,000 blocks of an equal size sequentially to the HDD. Table II demonstrates the performance of the hard disks benchmarked in relation to

![](_page_6_Figure_0.png)

![](_page_6_Figure_1.png)

their generated disk models for writing to the start of the disk and also starting at a 200 GB offset.

We remind the reader that since the outer tracks are more densely populated, the operations in Tables II(a) and (b) are performed slightly quicker than in Tables II(c) and (d). In both instances, our model predicts the performance of the hard drive to within approximately 5% of the observed timing.

As larger block sizes are used (64 blocks = 32 KB) our model starts to become slightly less accurate, due to our basic approximation of disk rotational latency. With the cache disabled, after each read (or write), the disk must complete a whole rotation before it is ready to read the next requested block, which adds a large overhead to operations that would otherwise be very small. This is another issue we hope to address in future work, and this inaccuracy will become less apparent when the disk's cache is modelled (as read-ahead caching will assume the next block will be accessed next, prefetching the data in a single rotation).

For the block striped benchmark we see very similar performance to the sequential test. Table III shows a similar pattern to previous data, where using a larger block size is slightly slower (although more data is read, meaning there is a higher disk throughput). We also see a similar effect when writing to the innermost tracks of the disk (Tables III (c) and (d)), where the maximum available bandwidth is lower. Similar to the sequential experiments, we see a greater level of inaccuracy at higher block counts due to our simplistic modelling of disk rotation.

The final experiment we report on compares the time taken to perform 1,000 random seek operations with a randomised block count, between 1 and a specified maximum. Figure 4 shows the results for both disks using read and write operations at randomised offsets. On average, each complete execution reads or writes (block count × 1000)/2 blocks. We note that the results for the random test, with a fixed block size, report near identical timings; since the time spent seeking is at least one order of magnitude larger than the time taken to read the data, changing the block size has a negligible effect on total time.

For the two disks, we see that the S320 performs almost equally for both read and write operations whereas the M250 is nearly seven seconds slower for write operations. In both cases our simulation is within 10% of the observed execution time, and follows the trend of the data very closely. Again, we believe our simplified modelling of rotational latency (where we assume half a rotation is required) may account for this error. We believe we can reduce this error in future work using a more complex model of disk rotation timing.

## VI. CONCLUSION

Efficiently and accurately predicting the performance of parallel scientific applications is an incredibly difficult task, often attempted through the use of simulation frameworks. The modularised approach of frameworks such as SST allows users to add components to augment their simulations, providing a better overall view of how an application may perform on a complete supercomputer.

In this paper we report on the initial development of DFSsim, a parallel file system simulator. We hope that through this framework we will be able to investigate the effects of different hardware and software configurations on a system. We begin this work through the modelling of a single HDD (which may be used as an OST or as an element of a RAID system that may then be used as an OST).

Specifically, we have demonstrated the ability of our tool to estimate the underlying characteristics of a hard disk's geometry, including how data is positioned on the disk platters; and how the disk's head seeks between different tracks. Using this information, we have built a simulation using a POSIX-like interface to allow applications to interact with our simulation without significant source code changes. We have demonstrated that over the course of an execution of 1,000 function calls, our simulation is within 10% of the observed time on two different HDDs for seek-heavy operations, and within 5% of the observed I/O time for sequential reading and writing tasks.

In future work we aim to extend our model further, discovering information about how the disk controller makes use of the on-board cache to improve both read and write behaviours.

We then intend to build upon this by implementing a basic simulation of the Linux ext4 file system, enabling real applications to utilise (via an LD_PRELOAD style library) a simulated disk in place of a real HDD, allowing for the evaluation of alternative I/O hardware and software configurations without the use of a simulation framework (e.g. SST). Finally, we hope to build a simulation of a parallel file system (specifically, Lustre) where the individual OSTs utilise the ext4 file system, and incorporate this into the SST framework, allowing parallel simulations written for SST to make use of many of the parallel I/O features of the Message Passing Interface (MPI-IO [26]).

## ACKNOWLEDGMENTS

This work is supported in part by The Royal Society through their Industry Fellowship Scheme (IF090020/AM).

## REFERENCES

- [1] A. Alexandrov, M. F. Ionescu, K. E. Schauser, and C. Scheiman, "LogGP: Incorporating Long Messages into the LogP Model – One Step Closer Towards a Realistic Model for Parallel Computation," in *Proceedings of the 7th Annual ACM Symposium on Parallel Algorithms and Architectures*, ser. SPAA '95. New York, NY, USA: ACM, 1995, pp. 95– 105.
- [2] J. A. Davis, G. R. Mudalige, S. D. Hammond, J. A. Herdman, I. Miller, and S. A. Jarvis, "Predictive Analysis of a Hydrodynamics Application on Large-Scale CMP Clusters," *Computer Science – Research and Development*, vol. 26, no. 3–4, pp. 175–185, June 2011.
- [3] G. R. Mudalige, S. D. Hammond, J. A. Smith, and S. A. Jarvis, "Predictive Analysis and Optimisation of Pipelined Wavefront Computations," in *Proceedings of the 2009 IEEE International Symposium on Parallel & Distributed Process*ing, ser. IPDPS '09. Washington, DC, USA: IEEE Computer Society, 2009, pp. 1–8.
- [4] M. B. Giles, G. R. Mudalige, Z. Sharif, G. Markall, and P. H. Kelly, "Performance Analysis of the OP2 Framework on Many-Core Architectures," *SIGMETRICS Performance Evaluation Review*, vol. 38, no. 4, pp. 9–15, March 2011.
- [5] D. J. Kerbyson, A. Hoisie, and H. J. Wasserman, "A Performance Comparison Between the Earth Simulator and Other Terascale Systems on a Characteristic ASCI Workload: Research Articles," *Concurrency and Computation: Practive & Experience*, vol. 17, no. 10, pp. 1219–1238, August 2005.
- [6] S. Pennycook, S. Hammond, G. Mudalige, S. Wright, and S. Jarvis, "On the Acceleration of Wavefront Applications using Distributed Many-Core Architectures," *The Computer Journal*, vol. 55, no. 2, pp. 138–153, February 2012.
- [7] C. A. Moritz and M. I. Frank, "LoGPC: Modeling Network Contention in Message-Passing Programs," *SIGMETRICS Performance Evaluation Review*, vol. 26, no. 1, pp. 254–263, June 1998.
- [8] A. F. Rodrigues, K. S. Hemmert, B. W. Barrett, C. Kersey, R. Oldfield, M. Weston, R. Riesen, J. Cook, P. Rosenfeld, E. Cooper-Balis, and B. Jacob, "The Structural Simulation Toolkit," *SIGMETRICS Performance Evaluation Review*, vol. 38, no. 4, pp. 37–42, March 2011.
- [9] S. D. Hammond, G. R. Mudalige, J. A. Smith, S. A. Jarvis, J. A. Herdman, and A. Vadgama, "WARPP: A Toolkit for Simulating High-Performance Parallel Scientific Codes," in *Proceedings of the 2nd International Conference on Simulation Tools and Techniques*, ser. Simutools '09. ICST, Brussels, Belgium, Belgium: ICST (Institute for Computer Sciences, Social-Informatics and Telecommunications Engineering), 2009, pp. 19:1–19:10.

- [10] J. S. Bucy, J. Schindler, S. W. Schlosser, and G. R. Ganger, "The DiskSim Simulation Environment Version 4.0 Reference Manual," 2008.
- [11] J. Schindler and G. R. Ganger, "Automated Disk Drive Characterization," in *Proceedings of the ACM SIGMETRICS International Conference on Measurement and Modeling of Computer Systems*, ser. SIGMETRICS '00. New York, NY, USA: ACM, 2000, pp. 112–113.
- [12] W. Hsu and A. J. Smith, "The Performance Impact of I/O Optimizations and Disk Improvements," *IBM Journal of Research and Development*, vol. 48, no. 2, pp. 255–289, March 2004.
- [13] C. Ruemmler and J. Wilkes, "An Introduction to Disk Drive Modeling," *Computer*, vol. 27, no. 3, pp. 17–28, March 1994.
- [14] D. Thiebaut, H. S. Stone, and J. L. Wolf, "Improving Disk ´ Cache Hit-Ratios Through Cache Partitioning," *IEEE Transactions on Computers*, vol. 41, no. 6, pp. 665–676, June 1992.
- [15] Y. Zhu and Y. Hu, "Disk Built-in Caches: Evaluation on System Performance," in *The 11th IEEE/ACM International Symposium on Modeling, Analysis and Simulation of Computer Telecommunications Systems*, ser. MASCOTS '03, October 2003, pp. 306–313.
- [16] D. A. Patterson, G. Gibson, and R. H. Katz, "A Case for Redundant Arrays of Inexpensive Disks (RAID)," in *Proceedings of the ACM SIGMOD International Conference on Management of Data*, ser. SIGMOD '88. New York, NY, USA: ACM, 1988, pp. 109–116.
- [17] P. Schwan, "Lustre: Building a File System for 1000-node Clusters," http://lustre.org (accessed October 23, 2011), 2003.
- [18] F. Schmuck and R. Haskin, "GPFS: A Shared-Disk File System for Large Computing Clusters," in *Proceedings of the First USENIX Conference on File and Storage Technologies (FAST'02)*. Monterey, CA: USENIX Association Berkeley, CA, January 2002, pp. 231–244.

- [19] D. Nagle, D. Serenyi, and A. Matthews, "The Panasas ActiveScale Storage Cluster: Delivering Scalable High Bandwidth Storage," in *Proceedings of the 16th ACM/IEEE International Conference for High Performance Computing, Networking, Storage, and Analysis*, ser. SC '04. Washington, DC, USA: IEEE Computer Society, 2004, p. 53.
- [20] C. A. Thekkath, J. Wilkes, and E. D. Lazowska, "Techniques for File System Simulation," *Software: Practice and Experience*, vol. 24, no. 11, pp. 981–999, 1994.
- [21] E. Molina-Estolano, C. Maltzahn, J. Bent, and S. A. Brandt, "Building a Parallel File System Simulator," *Journal of Physics: Conference Series*, vol. 180, no. 1, 2009.
- [22] N. Liu, J. Cope, P. H. Carns, C. D. Carothers, R. B. Ross, G. Grider, A. Crume, and C. Maltzahn, "On the Role of Burst Buffers in Leadership-Class Storage Systems," in *Proceedings of the 28th IEEE Conference on Massive Data Storage*, ser. MSST '12. IEEE, 2012, pp. 1–11.
- [23] N. Liu, C. Carothers, J. Cope, P. Carns, R. Ross, A. Crume, and C. Maltzahn, "Modeling a Leadership-Scale Storage System," in *Proceedings of the 9th International Conference on Parallel Processing and Applied Mathematics – Volume Part I*, ser. PPAM '11. Berlin, Heidelberg: Springer-Verlag, 2012, pp. 10–19.
- [24] P. H. Carns, B. W. Settlemyer, and W. B. Ligon, III, "Using Server-to-Server Communication in Parallel File Systems to Simplify Consistency and Improve Performance," in *Proceedings of the 20th ACM/IEEE International Conference for High Performance Computing, Networking, Storage, and Analysis*, ser. SC '08. Piscataway, NJ, USA: IEEE Press, 2008, pp. 6:1–6:8.
- [25] T. Nishimura, "Tables of 64-bit Mersenne Twisters," ACM *Transactions on Modeling and Computer Simulation*, vol. 10, no. 4, pp. 348–357, October 2000.
- [26] R. Thakur, E. Lusk, and W. Gropp, *ROMIO: A High-Performance, Portable MPI-IO Implementation*, Argonne, IL, 1997.

