# Enabling High-Throughput Parallel I/O in Particle-in-Cell Monte Carlo Simulations with openPMD and Darshan I/O Monitoring

Jeremy J. Williams1 , Daniel Medeiros1 , Stefan Costea2 , David Tskhakaya3 , Franz Poeschel4 , Rene Widera ´ 4 ,

Axel Huebl5 , Scott Klasky6 , Norbert Podhorszki6 , Leon Kos2 , Ales Podolnik3 , Jakub Hromadka3 ,

Tapish Narwal4 , Klaus Steiniger4 , Michael Bussmann4 , Erwin Laure7 , Stefano Markidis1

1*KTH Royal Institute of Technology, Sweden*; 2*LeCAD, University of Ljubljana, Slovenia*;

3 *Institute of Plasma Physics of the CAS, Czech Republic*; 4*Helmholtz-Zentrum Dresden-Rossendorf, Germany*;

5*Lawrence Berkeley National Laboratory, USA*; 6*Oak Ridge National Laboratory, USA*

7*Max Planck Computing and Data Facility, Germany*

*Abstract*—Large-scale HPC simulations of plasma dynamics in fusion devices require efficient parallel I/O to avoid slowing down the simulation and to enable the post-processing of critical information. Such complex simulations lacking parallel I/O capabilities may encounter performance bottlenecks, hindering their effectiveness in data-intensive computing tasks. In this work, we focus on introducing and enhancing the efficiency of parallel I/O operations in Particle-in-Cell Monte Carlo simulations. We first evaluate the scalability of BIT1, a massivelyparallel electrostatic PIC MC code, determining its initial write throughput capabilities and performance bottlenecks using an HPC I/O performance monitoring tool, Darshan. We design and develop an adaptor to the openPMD I/O interface that allows us to stream PIC particle and field information to I/O using the BP4 backend, aggressively optimized for I/O efficiency, including the highly efficient ADIOS2 interface. Next, we explore advanced optimization techniques such as data compression, aggregation, and Lustre file striping, achieving write throughput improvements while enhancing data storage efficiency. Finally, we analyze the enhanced high-throughput parallel I/O and storage capabilities achieved through the integration of openPMD with rapid metadata extraction in BP4 format. Our study demonstrates that the integration of openPMD and advanced I/O optimizations significantly enhances BIT1's I/O performance and storage capabilities, successfully introducing high throughput parallel I/O and surpassing the capabilities of traditional file I/O.

*Index Terms*—openPMD, Darshan, ADIOS2, Parallel I/O, Efficient Data Processing, Distributed Storage, Large-Scale PIC Simulations

# I. INTRODUCTION

Large-scale plasma simulations on high-performance systems continue to revolutionize our understanding of complex physical phenomena, particularly in the realm of fusion energy research. These simulations enable scientists to delve into the dynamics of plasma, crucial for optimizing the performance and safety of fusion reactors. From investigating turbulence and instabilities to probing confinement properties, these simulations offer invaluable insights that pave the way for advancements in sustainable energy production. However, the efficiency of these simulations heavily relies on efficient data handling and management, making high-performance I/O systems indispensable. These systems not only facilitate the seamless flow of data during simulations but also play a pivotal role in ensuring instantaneous post-processing of critical information.

Introducing parallel I/O in Particle-in-Cell (PIC) Monte Carlo (MC) simulations is particularly significant as it enables the efficient handling of data streams from multiple computational processes concurrently. This parallel approach enhances throughput, reducing the time required for data storage and retrieval, thereby accelerating the pace of scientific discovery, and expanding the scope of simulations. Despite the remarkable strides in computing capabilities, the persistent challenge lies in mitigating the performance bottleneck posed by I/O systems, which can impede the pace of scientific discovery and limit the scope of PIC MC simulations.

The openPMD standard [1] aims to solve the issue of portability of exchange particle and mesh based data from scientific simulations and experiments by providing a minimal set of meta information, supporting mutiple backends such as HDF5, ADIOS1, ADIOS2 and JSON in both serial or MPI-based workflows. BIT1 is a parallel plasma simulation electrostatic PIC MC code that currently contains I/O bottlenecks, and currently do not implement the openPMD standard.

In this work, we focus on introducing and enhancing throughput parallel I/O in BIT1, achieved through assessing and monitoring traditional file I/O performance using the Darshan tool, integrating the openPMD standard, facilitating efficient I/O operations, supporting parallel workflows, and minimizing data and storage on the file system. The contributions of this work include:

- We evaluate the performance of traditional file I/O in BIT1 with diagnostics activated.
- We critically discuss how the usage of a standard for naming schema can benefit a plasma simulation application.
- We implement an I/O adaptor for the openPMD I/O interface that uses ADIOS2 BP4 as I/O interface.

<sup>86</sup>

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:21:14 UTC from IEEE Xplore. Restrictions apply.

- We show that our high-throughput parallel I/O approach offers significant benefits on the POSIX interface.
- We analyze the impact of varying the number of aggregators, using data compressors, and explore optimization strategies for the BIT1 storage, focusing on Lustre file striping parameters such as stripe counts and sizes.

The remainder of this paper is organized as follows. Section 2 provides background information on ADIOS Version 2, openPMD Standard & openPMD-api, and BIT1's I/O strategies. Section 3 details our methodology and the experimental setup, including modifications made to BIT1 for this work. Performance results are presented in Section 4, including benchmarking, I/O costs per process analysis, data compression, aggregation, and Lustre file striping. Related work is discussed in Section 5. Finally, Section 6 contains the discussion, conclusion and future work.

# II. BACKGROUND

The PIC method is a numerical approach used to model plasma behavior. The method simulates particle dynamics in one to three-dimensions (1-3D) in a usual space and typically three dimensions (3V) in the velocity space. For plasma edge applications, the PIC method is usually complemented by MC routines for simulation of particle collisions and their interaction with the plasma device chamber walls. There are five phases to the computational PIC cycle: plasma density calculation using particle-to-grid interpolation, a density smoothing process to eliminate spurious frequencies, a field solver solving a linear system for electric and magnetic fields, addressing particle collisions and wall interactions with a MC technique, and advancing particle positions and velocities through time.

The application tool used in this work, BIT1, has a workflow used to simulate the plasma edge [2]–[4], plasma behavior in the tokamak divertor and is designed for large-scale plasma simulations on high-performance computing (HPC) systems. BIT1 is a 1D3V electrostatic PIC MC code used for plasma, impurity and neutral transport in a 1D magnetic flux tubes of the magnetic confinement fusion plasma edge. Despite low dimensional BIT1 can capture large number of kinetic processes and enable corresponding pioneering studies [5]. The Input to BIT1 represents a relatively small (1-3 kB) file read by all processes. The output corresponds to three different processes defined by five critical input parameters:

- datfile: Captures the system's diagnostic snapshot at a specific time step.
- dmpstep: Determines when the simulated system's current state is saved, indicating the preservation of particle states or time steps.
- mvflag: Represents a flag for activating time-dependant diagnostics of plasma profiles and particle angular, velocity and energy distribution functions. If > 0 it determines the number of time steps steps at which time dependent diagnostics are averaged.
- mvStep: Counter time steps for the interval between the time-dependant diagnostics.

- last step: Marks the time step at which the code concludes, saving the present state on the disk and terminating the simulation.
While the original version of BIT1's serial output functioned well for runs using up to 20,000 MPI Processes, larger simulations presented challenges. Beyond this threshold, the output process demanded considerably more time and frequently resulted in corrupted files. To ensure the accuracy of output files and optimize performance for extensive simulations, novel parallel I/O methods will need to be implemented in BIT1.

## *A. ADIOS Version 2*

The Adaptable Input Output System version 2 (ADIOS2) is an open-source framework designed for scalable parallel I/O. It supports the usage of C, C++, Fortran, and Python across various device platforms, including supercomputers, personal computers, and cloud systems. Its unified application programming interface (API) emphasizes n-dimensional variables, attributes, and steps, abstracting low-level details for efficient data transportation in applications such as checkpoint-restart storage, code-coupling data streaming, and in situ analysis and visualization workflows [6].

One of the most relevant features of ADIOS2 is the ability to choose the processing virtual engine. These engines relates to how the data will be read and written, and also gives the users different parameters to be set. These engines are the BP5, BP4, BP3, HDF5, Sustainable Staging Transport, Strong Staging Coupler, the DataMan, and the Inline engines. This work explores the usage of the BP4 engine. This is because BP4 prioritizes I/O efficiency at a large scale through aggressive optimization, while BP5 incorporates certain compromises to exert tighter control over the host memory usage.

# *B. openPMD Standard & openPMD-api*

The openPMD standard [1], known as the open standard for particle-mesh data files, provides portability for exchanging particle and mesh-based data from scientific simulations. It offers minimal meta information and supports diverse backends, including HDF5, ADIOS1, ADIOS2, and JSON, in both serial and MPI-based workflows. The openPMD-api library serves as a reference API for openPMD data handling [1], [7] and scientific I/O, as depicted in [8], supporting various backends such as HDF5, ADIOS2, and JSON. It accommodates both serial and MPI-parallel workflows, facilitating seamless writing and reading across different file formats.

In openPMD, a record is a physical quantity of arbitrary dimensionality (rank), potentially with multiple record components (e.g., scalars, vectors, tensors). These records share common properties, e.g., describing an electric or density field or particle property. Records may be structured as meshes (ndimensional arrays) or not, the latter case being the storage of particle species in 1D arrays, where each row represents a particle.

Updates to the values of the meshes or particle species is named as an iteration, and can be used to store the evolution of records over the time. Finally, the collection of iterations are named series, in which openPMD-api focuses on implementing many backends and encoding strategies.

#### *C. Fundamental Library and Interface*

The Standard Input/Output (stdio) library is a fundamental component in many programming languages, including C and C++, and designed for handling interactions with files or streams (through functions such as fopen, fread, fprintf) and to the "stdout". This library plays a significant role in basic I/O operations within the BIT1 code: when it is used within BIT1, it normally handles tasks as reading user input for simulation parameters, providing progress updates during the simulation execution, and basic logging. However, the usage of stdio in extreme-scale PIC MC simulation codes might not be the most efficient solution for extreme-scale PIC MC Simulation codes.

Meanwhile, the Portable Operating System Interface (POSIX) defines interface between an operating system and application programs, providing compatibility among operating systems, which is often related to file consistency guarantees. It includes a set of APIs for tasks such as file I/O, process management, and inter-process communication. POSIX threads could be used to parallelized certain aspects of the code, improving its performance on multi-core systems and may be leveraged for handling file-related operations in a portable and standardized manner. Many flavours of MPI (used by ADIOS2 BP engines) implementations are POSIXneutral, which means that it is compatible with most operating systems.

## III. METHODOLOGY & EXPERIMENTAL SETUP

Building upon our focus outlined in this work, which centers on integrating the openPMD standard, facilitating efficient I/O operations, supporting parallel workflows, and minimizing data storage, we detail the specific modifications implemented within BIT1.

#### *A. openPMD & openPMD-api Integration*

BIT1 is a 1D3V PIC code implemented in C, where simulations are executed in one-dimensional space with the utilization of three dimensions for particle velocities. The openPMDapi parallel I/O library has been seamlessly integrated into BIT1 to enhance its I/O functionality.

In [9], a new header file, bit1.hpp, written in C++, has been created to integrate openPMD into BIT1, providing accommodation for the functions and global variables associated with the openPMD standard. In this header file, key components include the combination of the original BIT1 header, originally written in C, a vital "Series" object acting as the root of the openPMD output, extending across all data for all iterations [10]. This object is made universally accessible throughout the code. Additionally, a collection of vectors, whether singular or nested, of type float or unsigned long is used to store data until either flush() is invoked or until the "iteration" is formally concluded. It is important to note that once an "iteration" is closed, reopening it is not required [11]. Accompanying these structures are dedicated functions for converting data arrays into openPMD data objects and for the subsequent storage of these objects onto the disk.

#### *B. Checkpointing & Compressors*

BIT1 operates with minimal diagnostics, as evidenced by the time history of the total particle number [12]. Additionally, depending on the selected options in the input file, it can log particle and power fluxes to the wall with minor computational overhead. Furthermore, BIT1 has the capability to periodically save the system's state for checkpointing and restart purposes.

To enhance data transmission speed and reduce the volume of large datasets within BIT1 simulations, Blosc data compression has been integrated [13], [14], which can be compared to the high-quality data compressor bzip2 [15], [16]. This implementation utilizes a "TOML-based dynamic configuration" with a "group-based iteration encoding with steps" memory strategy [17], as shown in [9].

To use these functionalities using openPMD, all MPI ranks must adhere to a step-by-step procedure, unless specified otherwise. First, the Blosc compressor configuration is passed (or not) to the constructor of the Series class, then the file must be opened for writing to disk by creating a "Series" object with the filename's path, access mode, and the global MPI communicator as arguments. The file's extension dictates the engine used by openPMD for data storage. Subsequently, the iteration holding the data must be explicitly opened.

For BIT1, iteration 0 is chosen to record data that is periodically overwritten, such as the latest system state for simulation continuation. Following this, any function that stores data with openPMD must be called, with each MPI rank creating a local vector to store values for subsequent saving. These local vectors are then appended to global vectors, ensuring data persistence until flush() is called. Once data accumulation is complete, the accumulated data is flushed to disk in a single action for optimal I/O efficiency. The iteration is then explicitly closed, and if no further iterations are needed, the series is closed, and all global vectors are cleared.

When BIT1 utilizes openPMD, the contents of the function any_function_save() involve creating vectors locally by each MPI rank to store values intended for saving. These local vectors are then appended to global vectors and subsequently cleared. The length of the local vector is referred to as the local extent. To save to the disk, openPMD requires both the local extent and the offset of each MPI rank in the global extent of the array to be saved, and this information is obtained by calling MPI functions. Additionally, openPMDspecific objects such as "Iteration", into which data is saved, "Datatype" of the vector to be saved to disk, "Global Extent", "Offset" and "Local Extent" objects, "Dataset", and "Record Component" are created to facilitate the required compiler linking process. Finally, if the local vector is not empty, it is stored to disk.

It is crucial to note that key operations between storeChunk() and flush() must not modify the refer-

![](_page_3_Figure_0.png)

Fig. 1: BIT1 I/O Workflow with openPMD using ADIOS2 BP4 Engine

enced data, as emphasized throughout the openPMD documentation. This integrated approach enhances the capabilities of BIT1 and facilitates efficient data storage and retrieval, ensuring robust checkpointing and restoration mechanisms.

#### *C. Use Case & Experimental Environment*

In this work, we focus on enhancing both scalability and I/O efficiency in BIT1 using openPMD and ADIOS2 backends. We simulate neutral particle ionization resulting from interactions with electrons in upcoming magnetic confinement fusion devices like ITER and DEMO. The scenario involves an unbounded unmagnetized plasma consisting of electrons, D+ ions and D neutrals. Due to ionization, neutral concentration decreases with time according to ∂n/∂t = nneR, where n, ne and R are neutral particles, plasma densities and ionization rate coefficient, respectively. We use a one-dimensional geometry with 100K cells, three plasma species (e electrons, D+ ions and D neutrals), and 10M particles per cell per species. The total number of particles in the system is 30M. Unless differently specified, we simulate up to 200K time steps. An important point of this test is that it does not use the Field solver and smoother phases (shown in [18], [19]).

We simulate and evaluate the I/O performance of BIT1 on the following three distinct systems:

- Discoverer, a petascale EuroHPC supercomputer, features a CPU partition with 1128 compute nodes. Each node is equipped with two AMD EPYC 7H12 64-Core processors, 256 GB DDR4 SDRAM (on regular nodes), 1TB DDR4 SDRAM (on fat nodes), interconnected using Ethernet Controller I350 with 10 GiB/s Bandwidth and Mellanox ConnectX-6 InfiniBand with the Dragonfly+ topology, amounting to 200 GiB/s Bandwidth. For storage, Discoverer has a Network File System (over Ethernet) with 4.4 TB, and a Lustre File System (LFS) with 2.1 PB in capacity and 4 Object Storage Targets (OSTs). The operating system (OS) is Red Hat Enterprise Linux release 8.4, and all the applications were compiled with GCC 11.4.0 and MPI library, MPICH 4.1.2 for intra-node communication.
- Dardel, an HPE Cray EX supercomputer, features a CPU partition with 1270 compute nodes. Each node is equipped with two AMD EPYC™ Zen2 2.25 GHz 64-core processors, 256 GB DRAM, and interconnected using an HPE Slingshot network with the Dragonfly topology, amounting to 200

GiB/s Bandwidth. In terms of storage, Dardel has a LFS with 12 PB in capacity and 48 OSTs. The OS is SUSE Linux Enterprise Server 15 SP3, and all applications were compiled with GCC 11.2, openPMD 0.15.2, ADIOS2 2.10.0 (with Blosc and bzip2 compression enabled) and Cray MPICH 8.1 as the MPI flavor for intra-node communication. • Vega, a petascale EuroHPC supercomputer, features a CPU

- partition with 960 compute nodes. Each node is equipped with two AMD EPYC 7H12 64-Core processors, 256 GB DDR4 SDRAM (80%/nodes), 1TB DDR4 SDRAM (20%/nodes), interconnected using Mellanox ConnectX-6 InfiniBand HDR100 with a Dragonfly+ topology, amounting up to 500 GiB/s Bandwidth. For storage, Vega has a Ceph File System (CephFS) with 23 PB, and LFS with 1 PB in capacity and 80 OSTs. The OS is Red Hat Enterprise Linux 8, and all applications were compiled with GCC 12.3.0 and MPI library, OpenMPI 4.1.2.1 for intra-node communication.
#### *D. I/O Workflow & Monitoring*

As pointed by [18], BIT1 performs serial I/O during every simulation. Similar to [8], a workflow has been implemented by utilizing the selected ADIOS2 engines with the required output extensions (.bp, .bp4, and .bp5 respectively). For each extension, a unique ADIOS2 file (or directory) is created right after each simulation run, containing one or more data files (data.0, data.1 ... data.N, data.N+1), a metadata file (md.0), an index table (md.idx), and if enabled, a profiling file (profiling.json). However, for BP5, there is a second metadata file (mmd.0) in the directory, which BP4 and BP3 do not have. Figure 1 displays the BIT1 I/O Workflow with openPMD using ADIOS2 BP4 Engine, output extension directory data_file.bp4 and default profiling enabled.

Among the many I/O profilers, Darshan stands out as a tool of choice to provide insight into how applications interact with underlying storage systems. Darshan is a performance monitoring tool specifically designed for analyzing both serial and parallel I/O workloads [20]. It collects various statistics during runtime, including data transfer sizes, access patterns, and file metadata operations. These metrics are relevant for understanding I/O bottlenecks (further discovered in [18]) and fine-tuning application performance. We evaluate the I/O performance of BIT1 in terms of write throughput by extracting the throughput and amount of data stored by each file on the file system using Darshan 3.4.2 logs.

In our tests, we initially evaluate BIT1 with a standard I/O setup (BIT1 Original I/O) to assess the impact of scaling the number of nodes on Discoverer, Dardel, and Vega CPU LFS. Next, focusing on Dardel's LFS, we use different BIT1 configurations and compare BIT1 Original I/O with others using openPMD and ADIOS2 engine (BP4), aggregators (1 to 25600), data compressors (Blosc, bzip2), Lustre stripe counts (1, 2, 4, 8, 16, 32, 48), Lustre stripe sizes (1MB, 2MB, 4MB, 8MB, 16MB), and the number of parallel writers.

## IV. PERFORMANCE RESULTS

We begin this work by investigating the I/O performance when BIT1 diagnostics are activated. To better understand scalable I/O performance, we use a simulation of 200K time steps, and we have diagnostics output (with BIT1 I/O flags slow for plasma profiles and distribution functions, slow1 for self-consistent atomic collision diagnostics, generating the required .dat files) every 1K cycles and checkpointing files (so-called .dmp files) every 10K cycles. The read operations are limited to read the simulation input files. In this work, we focus on analysing the performance of the write operations in BIT1.

![](_page_4_Figure_4.png)

Fig. 2: BIT1 Original File I/O Write Throughput, on Discoverer, Dardel and Vega CPU LFS, up to 200 Nodes, measured in GiB/s.

Fig. 2 displays the performance of traditional file I/O in BIT1 on Discoverer, Dardel, and Vega CPU LFS. The Discoverer CPU exhibits fluctuating performance, declining by 23% from 0.26 GiB/s for 1 node to 0.20 GiB/s for 200 nodes, indicating poor scalability. Conversely, the Dardel CPU shows improved performance, with write throughput increasing from 0.09 GiB/s for 1 node to 0.41 GiB/s for 200 nodes, suggesting better suitability for parallelism. However, the Vega CPU demonstrates inconsistent performance, lacking clear scaling behavior. Given that Dardel displays the highest Write Throughput on larger nodes, we will continue our investigation using the Dardel CPU LFS, which is also applicable on the other two systems (Discoverer and Vega CPU LFS).

In Fig. 3 BIT1 Original I/O Write Throughput up to 200 nodes, performs serial I/O. The write throughput increases for

![](_page_4_Figure_8.png)

Fig. 3: BIT1 Original File I/O and openPMD + BP4 Write Throughput on Dardel up to 200 Nodes, measured in GiB/s.

small runs until the peak throughput is reached. For large runs, the I/O write throughput decreases as the cost associated with metadata write increases [18]. Unlike BIT1's traditional file I/O, where the write throughput decreases primarily due to the escalating cost associated with metadata write, BIT1 openPMD + BP4 maintains a more stable throughput. This is attributed to the parallel I/O strategy applied to distribute the workload efficiently across multiple nodes, mitigating the adverse effects of metadata write overhead.

#### *A. Benchmarking*

Benchmarking, a crucial process in performance evaluation, efficiency assessment, and quality comparison, involves comparing systems, devices, or processes against established benchmarks. The IOR benchmark is a configurable tool that can be tailored to simulate the read and write operations of real-world applications. It provides options for customizing various aspects such as I/O protocols, modes, and file sizes. Essentially, IOR facilitates data reading and writing from either an exclusive or shared file.

Below are relevant IOR parameters [21]:

- -N (NumTasks): Specifies the task count for the IOR benchmark.
- -a (Api): Determines the API option to be used for I/O [POSIX|MPIIO|HDF5|. . . |RADOS].
- -F (FilePerProc): Enables file-per-process mode.
- -C (ReorderTasksConstant): Switches task ordering to n+1 for readback.
- -e (Fsync): Execute "fsync" when closing POSIX write operations.

Using the IOR benchmark, we evaluate BIT1's performance in the Dardel CPU LFS system, aiming to identify areas for improvement.

Fig. 4 displays the I/O performance results of the BIT1 Original I/O and BIT1 openPMD + BP4 configurations, compared to the IOR benchmarking results, using the commands outlined in Table I, on the Dardel CPU LFS system, for up to 200 nodes. Analysis reveals distinct performance trends between the two BIT1 configurations. BIT1 Original I/O exhibits a low initial write throughput of 0.09 GiB/s, gradually

![](_page_5_Figure_0.png)

TABLE I: Command lines used to run IOR [21], [22] with parameters, -N, -a, -F, -C, and -e on Dardel LFS (200 nodes).

increasing with node count but failing to achieve competitive levels compared to the IOR benchmarks. Conversely, BIT1 openPMD + BP4 with aggregation demonstrates superior performance, starting with a higher write throughput of 0.6 GiB/s and exhibiting a notably steeper increase with additional nodes. This consistent improvement highlights the configuration's enhanced scalability, parallelization capabilities, and effectiveness in minimizing waiting times for shared I/O resources during BIT1 simulations.

![](_page_5_Figure_3.png)

Fig. 4: BIT1 I/O Write Throughput on Dardel up to 200 Nodes, measured in GiB/s.

# *B. I/O Costs Per Process*

Reducing I/O function runtime is essential for enhancing the efficiency, scalability, and cost-effectiveness of computational BIT1 simulations. By minimizing the time spent on BIT1 I/O operations, we can accelerate data processing, optimize resource utilization, and facilitate the handling of larger datasets and more complex simulations [23], [24].

As discovered in [18], [19], the peak I/O write throughput depends on the problem size, and after the peak I/O is reached, the I/O performance degrades as the metadata writing cost increases on large runs. To understand the benefits of using openPMD with ADIOS2 backends, we investigate the time spent in I/O functions on 200 nodes, comparing BIT1's original I/O method with openPMD using BP4. Figure 5 displays the normalized results of average I/O reads, writes, and metadata costs per process during BIT1 simulations on 200 nodes.

Analyzing the results reveals that the integration of openPMD with ADIOS2 backends, particularly employing BP4, has yielded remarkable enhancements in BIT1. Foremost among these improvements is the substantial reduction in metadata overhead. Previously, the average time spent on metadata operations per process stood at 17.868 seconds in the BIT1 Original I/O simulation. However, with openPMD + BP4, this time plummeted to a mere 0.014 seconds per process, representing an astounding reduction of approximately 99.92%. Concurrently, there has been a notable enhancement in write capability. In the BIT1 Original I/O execution, the average time spent on write operations per process was 1.043 seconds, which significantly decreased to 0.009 seconds with openPMD + BP4, highlighting a reduction of around 99.14%.

![](_page_5_Figure_10.png)

Fig. 5: BIT1 Average I/O Cost Per Process on Dardel for Reads, Metadata and Writes on 200 nodes, normalized.

Importantly, the time spent on reads remains consistent, primarily due to checkpointing, where files are saved and stored for restarting the simulation. This consistency shows the reliability and stability of the read operations, enabling seamless continuation of simulations while focusing on the significant improvements in metadata handling and write performance. These improvements directly contribute to overall I/O performance enhancement by efficiently managing metadata and improving write performance. As a result, BIT1 simulations benefit from the effectiveness of using openPMD with ADIOS2 backends in balancing metadata reduction and writing capability, thereby directly contributing to overall I/O performance enhancement by efficiently managing metadata and improving write performance.

## *C. Aggregation*

For optimal I/O performance in BIT1, "N" processes must distribute their output across "M" files to maximize the file system's throughput, minimize the overhead of multiple processes writing to a single file, and prevent overloading the file system with excessive files. In ADIOS2, each node is allocated (or fixed) one aggregator (AGGR), leading to a single shared file among MPI processes per node [25]. An essential parameter (also used with the BP5 engine) in this context is "OPENPMD ADIOS2 BP5 NumAgg," which dictates the desired number of output files (aggregators) to be written to disk, ensuring efficient I/O performance even as the number of MPI processes varies. Fig. 6 displays the scaling results obtained from multiple BIT1 openPMD simulations using the BP4 engine, with a fixed value set for "OPENPMD ADIOS2 BP5 NumAgg" to determine the

91

![](_page_6_Figure_0.png)

Fig. 6: BIT1 openPMD + BP4 I/O Write Throughput and Aggregators on Dardel, measured on 200 nodes, in GiB/s.

optimal number of aggregators. Notably, as the number of aggregators increases, there is a consistent improvement in write throughput until reaching a peak at 400 aggregators (equivalent to two aggregators per node), achieving 15.80 GiB/s. Beyond this point, there is a slight decline in throughput with further aggregation, even though at the highest tested aggregation (25600), the write throughput remains significantly higher than the starting point, at 3.87 GiB/s. This demonstrates a notable increase in write throughput, highlighting the scalability benefits from 0.59 GiB/s for 1 aggregator to 15.80 GiB/s for 400 aggregators. Moreover, at 25600 aggregators, the throughput notably surpasses BIT1 Original I/O performance (0.41 GiB/s) with the same number of files, highlighting the effectiveness of the BIT1 openPMD + BP4 approach in enhancing write operation performance under extreme aggregation scenarios.

![](_page_6_Figure_3.png)

Fig. 7: BIT1 I/O Write Throughput on Dardel for up to 200 Nodes, using the Blosc Compressor and one Aggregator, measured in GiB/s

#### *D. Data Compression*

In the BIT1 openPMD implementation and during ADIOS2 compilation, the Blosc and bzip2 compressors were chosen and enabled to enhance data transmission speed, reduce data size, and enable greater storage capacity in the file system [6], all while retaining essential information for each simulation. Fig 7 shows scaling results obtained from BIT1 I/O Write Throughput up to 200 Nodes with Blosc compression, and one Aggregator. As before, BIT1 Original I/O displays an inconsistent performance pattern as the number of nodes increases, eventually leading to a peak write throughput of approximately 0.54 GiB/s with 40 nodes, suggesting potential inefficiencies in utilizing computational resources at higher node counts. In contrast, both "BIT1 openPMD + BP4" configurations demonstrate enhanced scalability and efficiency, with improved performance and higher throughput observed from 1 to 10 nodes. Although compression and aggregation enhance data storage efficiency, they also introduce overhead, resulting in slightly reduced performance compared to the uncompressed configuration (BIT1 Original I/O) at higher node counts, which can be seen from 10 to 50 nodes.

Controlling ADIOS2 I/O behavior at runtime helps finetune our BIT1 simulation for large runs and shows greater potential for optimizing data management and processing [6], [8]. To do this, the environment variable "OPENPMD ADIOS2 HAVE PROFILING" is set to "1", providing a file (profiling.json) with profiling information at the end of each BIT1 simulation run.

Fig 8 displays profiling.json results on 200 nodes, where memory copy operation execution times are entirely eliminated for the BIT1 openPMD + BP4 configuration with Blosc compression and 1 AGGR. This indicates that the use of Blosc compression and 1 AGGR has effectively optimized (or streamlined) the data handling process to the extent that the time spent on memory copy operations is virtually eliminated.

![](_page_6_Figure_10.png)

Fig. 8: BIT1 openPMD + BP4 profiling.json results from Dardel on 200 nodes, showing memory copy operations executed in microseconds, with compression (blue) and without compression (red).

Table II displays the summary of write file scaling results for BIT1 Original without compression and BIT1 openPMD + BP4 using Blosc and Bzip2 compressors, all with varying numbers of aggregators. Analysis of the results reveals notable trends in file count and size across different configurations and node counts. In the BIT1 Original I/O setup with no compression and aggregation, the total number of written files increases significantly with the number of nodes, from 262 files for 1 node to 51,206 files with 200 nodes, while the average file size decreases as the number of nodes increases, from 1.9 MiB with 1 node to 13 KiB with 200 nodes, with a similar trend observed for maximum file size. Using compression, particularly the bzip2 compressor, alongside the openPMD + BP4 setup, leads to a substantial reduction in the total number of written files. Additionally, larger average file sizes are observed compared to the uncompressed BIT1 simulations, contributing to improved storage efficiency. For instance, on 200 nodes, the total written files decrease significantly from 6 files with 1 node to 205 files, with average file sizes ranging from 9.4 MiB to 81 MiB, and maximum file sizes varying widely from 476 MiB to 1.1 GiB.

Shared file strategies with 1 AGGR maintain a consistent total file count across all node counts, accompanied by increased average and maximum file sizes compared to using standard setups. For instance, in the configuration using bzip2 compression and 1 AGGR, total written files remain constant at 6 files across all node counts, with average file sizes increasing slightly from 81 MiB with 1 node to 326 MiB with 200 nodes, and maximum file sizes also increasing from 476 MiB to 1.1 GiB. This is achieved by setting the "OPENPMD ADIOS2 BP5 NumAgg" parameter to 1, ensuring that exactly one file is written on the disk for all MPI ranks. However, with the change in compression technique, particularly the Blosc compressor, alongside the openPMD + BP4 with 1 AGGR, total written files still remain constant at 6 files across all node counts with average file sizes decreasing slightly from 81 to 72 MiB for 1 node, reflecting an 11.11% reduction, and from 326 to 314 MiB for 200 nodes, indicating a 3.68% reduction on large runs. Additionally, maximum file sizes also decrease slightly from 476 to 422 MiB, representing an 11.43% reduction, with roughly no change observed at 1.1 GiB for 200 nodes.

![](_page_7_Figure_2.png)

TABLE II: BIT1 Writes Files on Dardel CPU LFS for up to 200 nodes across different configurations, showing the total number of files created along with their average and maximum sizes (in MiB).

# *E. Lustre File Striping*

Lustre file striping plays a crucial role in optimizing BIT1 storage performance. When a file is written to Lustre, it is divided into smaller segments called "stripes". These stripes are then systematically distributed across multiple OSTs. By separating the data across several OSTs, Lustre can leverage the aggregate throughput and I/O capabilities of these devices, enabling faster I/O operations [26], [27].

The selection of Lustre file striping configuration, which includes parameters such as the number of OSTs and the size of the stripes, has a direct impact on system performance. A well-tailored striping configuration can optimize throughput and reduce latency by efficiently distributing the workload across available storage resources [27]–[29].

| Lustre File Striping Command |
| --- |
| lfs setstripe -c 8 -S 16M io_openPMD |

TABLE III: Command line to configure Dardel's LFS to stripe newly created files within the "io openPMD" directory across 8 OSTs, with each stripe size set to 16,777,216 bytes (16 MiB).

The command line shown in Table III is used to configure Lustre file striping and set up Dardel's Lustre parallel file system. The command "lfs setstripe" determines how files are distributed across multiple OSTs. In this command, "-c 8" specifies that each file will be divided into 8 parts (stripes), while "-S 16M" indicates that each stripe will have a size of 16 MiB during creation in the "io openPMD" directory. To verify that the file striping configuration has been successfully applied, "lfs getstripe" command is used to extract this information. The output displayed in Listing 1 provides essential details about the file striping configuration. It reveals that the file "data.0" in the directory "io openPMD/dat file.bp4" is divided into 16 stripes, each with a size of 16,777,216 bytes (16 MiB), utilizing the raid0 striping pattern. Further details provided include the object directory index, object ID, associated group, and the utilization of 8 OSTs for file striping.

| $ lfs getstripe io_openPMD/dat_file.bp4/data.0 |  |  |  |
| --- | --- | --- | --- |
| io_openPMD/dat_file.bp4/data.0 |  |  |  |
| lmm_stripe_count: 8 |  |  |  |
| lmm_stripe_size: 16777216 |  |  |  |
| lmm_pattern: raid0 |  |  |  |
| lmm_layout_gen: 0 |  |  |  |
| lmm_stripe_offset: 17 |  |  |  |
| obdidx | objid | objid | group |
| 17 | 297315680 | 0x11b8ad60 | 0x700000400 |
| 19 | 297401760 | 0x11b9fda0 | 0x740000400 |
| 21 | 297299648 | 0x11b86ec0 | 0x800000400 |
| 23 | 297230944 | 0x11b76260 | 0x840000400 |
| 25 | 296891424 | 0x11b23420 | 0x900000400 |
| 27 | 297129552 | 0x11b5d650 | 0x940000400 |
| 29 | 294976177 | 0x1194fab1 | 0xa00000400 |
| 31 | 297343489 | 0x11b91a01 | 0xa40000400 |

Listing 1: Extracted Lustre file striping configuration for file "data.0" using the "lfs getstripe" command. The file is divided into 8 pieces (stripes), each with a size of 16,777,216 bytes (16 MiB), utilizing the raid0 (round-robin fashion) striping pattern. Detailed information such as Object Directory index, object ID, associated group, and the use of 8 OSTs for file striping.

Focusing on evaluating the write time spent and determining the optimal Lustre configuration across different Lustre stripe sizes and varying the number of OSTs, Figure 9 offers insights into the direct impact of system performance for BIT1 openPMD + BP4 configurations utilizing Lustre file striping, Blosc compression, and one AGGR on 200 nodes. Analyzing the scaling results reveals interesting findings. Smaller Lustre stripe sizes tend to yield better performance, particularly noticeable when employing a single OST, with optimal performance achieved at 0.0089s with a Lustre stripe size of 16MiB. However, the relationship between Lustre stripe size and write time varies significantly based on the number of OSTs employed. Interestingly, in some scenarios, increasing the number of OSTs led to reduced write times, indicating potential improvements in workload distribution and parallelism. For instance, with a Lustre stripe size of 4MiB, the write time decreases by approximately 4% when transitioning from 1 OST to 2 OSTs. Conversely, with a stripe size of 16MiB, the write time increases by approximately 7.87% with the same transition. Nonetheless, these trends are not uniform across all configurations, highlighting the need for tailored optimization strategies in Dardel CPU LFS.

![](_page_8_Figure_1.png)

Fig. 9: BIT1 openPMD + BP4 I/O Write Time Spent on Dardel CPU LFS (200 nodes) using Lustre File Striping with Blosc Compressor and one Aggregator, measured in seconds.

Moreover, diminishing returns were observed beyond a certain point, where further increasing OSTs provided minimal or negligible improvements in write time. Finding an optimal balance is essential to avoid unnecessary overhead. This suggests the importance of carefully fine-tuning Lustre configurations, especially with smaller stripe sizes, as a smaller number of OSTs may lead to more efficient performance for write operations in the BIT1 openPMD + BP4 configurations on large runs.

#### V. RELATED WORK

PIC codes are fundamental for plasma simulations, with significant efforts in development, analysis, optimization, and integration of modern standards like openPMD and ADIOS2. The use of openPMD and ADIOS2 has been shown to improve I/O performance. By utilizing the ADIOS2 library through the openPMD-api, performance numbers can be collected, and models can be built to enhance I/O performance [30]. ADIOS2 provides a framework for high-performance I/O, expanding on the legacy of earlier versions and offering C++ and Python APIs for scientific I/O with openPMD [6], [25]. It also offers an abstraction for high-performance I/O and supports features such as data staging and compression, leading to improved I/O workflows and data reduction [31]. Banerjee et al. [32] further highlighted an algorithmic and software pipeline for data compression with error guarantees, utilizing ADIOS2 for efficient parallel I/O workloads. Research has also shown that organizing large datasets efficiently can lead to improved analyses on HPC systems, further optimize I/O performance [33]. The concept of improving I/O performance has been a topic of interest in the field of computer science for several decades. Crockett [34] discussed file concepts for parallel I/O, highlighting the importance of efficient data storage and retrieval in parallel computing environments. Similarly, James et al. [35] introduced a distributed-directory scheme to achieve a scalable and coherent interface in parallel systems. Pioneering research by Berkeley University and Lawrence Livermore National Laboratory has laid the foundation for understanding PIC methods and their implementations, as documented in influential works by Birdsall and Langdon [36], [37]. One of the key features of the BIT1 code is its memory layout. The data layout was explained in [3], and a detailed explanation of the governing equations and algorithmic part is provided in [4], offering insights into the foundational principles driving BIT1's computational framework. Williams et al. conducted a detailed performance analysis of BIT1, leveraging various profiling tools to unravel its computational dynamics and identify potential optimization opportunities [18], [19]. This study sheds light on the complexities of BIT1's execution, providing valuable guidance for enhancing its performance. Recent advancements in data handling paradigms have revolutionized the I/O workflows of PIC simulations. Poeschel et al. [8] demonstrated the transformative potential of integrating openPMD and ADIOS2 into PIConGPU, transitioning from traditional file-based approaches to streamlined data pipelines.

## VI. DISCUSSION AND CONCLUSION

Our primary goal was to enhance the write output throughput and scalability of BIT1 performance. Central to our key efforts in this work was the integration of the openPMD standard, which serves as a foundation for efficient parallel write operations. By prioritizing support for parallel workflows and emphasizing the minimization of data and storage requirements on the file system, we have uncovered significant insights. Most importantly, it's worth noting that read operations were not a bottleneck that needed addressing, as checkpoints read very little data in BIT1.

Through comprehensive benchmarking and cost analysis using the Darshan I/O performance monitoring tool, we demonstrated remarkable scalability and write throughput improvements achievable with the openPMD integration, particularly notable with the ADIOS2 BP4 engine. Our exploration of data compression and aggregation techniques has highlighted crucial roles in enhancing data storage efficiency, even though these techniques introduce minor performance trade-offs, such as overhead. Our investigation into using Lustre file striping configurations has revealed a substantial impact on system performance. Notably, we observed that optimal performance varies depending on the number of OSTs, stripe sizes, and if data compression and aggregation techniques are used, especially within the context of BIT1 openPMD + BP4 configurations on large-scale runs.

Future research can enhance BIT1's capabilities by prioritizing openPMD integration (with ADIOS2), investigating parallel post processing performance benchmarks, particle load balancing, and continuing with checkpoint restarts towards evaluating and improving resilience capabilities. Moreover, future research should thoroughly investigate the utilization of other supported engines like the Sustainable Staging Transport (SST). The ADIOS2 SST engine enables the direct connection of data producers and consumers via the ADIOS2 write/read APIs, facilitating the movement of data between processes for in-situ processing, analysis, and visualization. These improvements would further minimize data and storage requirements, ultimately fostering more efficient and scalable BIT1 simulations.

#### REFERENCES

- [1] A. Huebl, R. Lehe, J.-L. Vay, D. P. Grote, I. Sbalzarini, S. Kuschel, D. Sagan, C. Mayes, F. P´erez, F. Koller, and M. Bussmann, "openPMD: A meta data standard for particle and mesh based data," 2015. Available at: https://www.openPMD.org, https://github.com/openPMD.
- [2] D. Tskhakaya and S. Kuhn, "The magnetised plasma-wall transition: Theory and pic simulation," Contributions to Plasma Physics, vol. 44, no. 5-6, pp. 564–570, 2004.
- [3] D. Tskhakaya and et al., "Optimization of pic codes by improved memory management," Journal of Computational Physics, vol. 225, no. 1, pp. 829–839, 2007.
- [4] D. Tskhakaya and et al., "Pic/mc code bit1 for plasma simulations on hpc," in 2010 18th Euromicro Conference on Parallel, Distributed and Network-based Processing, pp. 476–481, IEEE, 2010.
- [5] D. Tskhakaya, "One-dimensional plasma sheath model in front of the divertor plates," Plasma Physics and Controlled Fusion, vol. 59, no. 11, p. 114001, 2017.
- [6] D. Pugmire, N. Podhorszki, S. Klasky, M. Wolf, J. Kress, M. Kim, N. Thompson, J. Logan, R. Wang, K. Mehta, et al., "The adaptable io system (adios)," in In Situ Visualization for Computational Science, pp. 233–254, Springer, 2022.
- [7] A. Huebl, F. Poeschel, F. Koller, and J. Gu, "openPMD-api: C++ & Python API for Scientific I/O with openPMD," 06 2018. Available at: https://github.com/openPMD/openPMD-api.
- [8] F. Poeschel and et al., "Transitioning from file-based hpc workflows to streaming data pipelines with openpmd and adios2," in Smoky Mountains Computational Sciences and Engineering Conference, pp. 99–118, Springer, 2021.
- [9] I. of Plasma Physics of the CAS and P. Team, "Bit1 openpmd implementation using "toml-based dynamic configuration" with a "group based iteration encoding with steps" memory strategy," 2024. Available at: https://repo.tok.ipp.cas.cz/tskhakaya/bit1/source/writeparallel. cpp (updated: 2024-02-15).
- [10] openPMD, "openpmd-api structure," 2023. Available at: https:// github.com/openPMD/openPMD-api/blob/dev/examples/1 structure.cpp (updated: 2023-12-22).
- [11] openPMD, "openpmd-api writing," 2023. Available at: https://openpmd-api.readthedocs.io/en/latest/usage/parallel.html#writing (updated: 2023-12-22).
- [12] M. KOCAN and et al., "Particle simulations of the nonlinear electron ˇ dynamics in the classical pierce diode," Journal of plasma physics, vol. 72, no. 6, pp. 851–855, 2006.
- [13] T. B. Developers, "What is blosc?," 2023. Available at: https://www. blosc.org/pages/blosc-in-depth/ (accessed: 2023-12-22).
- [14] M. Zeyen, J. Ahrens, H. Hagen, K. Heitmann, and S. Habib, "Cosmological particle data compression in practice," in Proceedings of the In Situ Infrastructures on Enabling Extreme-Scale Analysis and Visualization, pp. 12–16, 2017.
- [15] J. Seward, "bzip2 and libbzip2," Available at: http://www.bzip.org,1996.
- [16] S. Julian, "The bzip2 and libbzip2 official homepage," Available at: https://cir.nii.ac.jp/all?q=http://sourceware.cygnus.com/bzip2/ , 2000.
- [17] B. file engine, "Memory management strategy," 2023. Available at: https://openpmd-api.readthedocs.io/en/0.15.2/backends/adios2.html# memory-usage (updated: 2023-12-22).
- [18] J. J. Williams, D. Tskhakaya, S. Costea, I. B. Peng, M. Garcia-Gasulla, and S. Markidis, "Leveraging hpc profiling and tracing tools to understand the performance of particle-in-cell monte carlo simulations,"

in European Conference on Parallel Processing, pp. 123–134, Springer, 2023.

- [19] J. J. Williams, F. Liu, D. Tskhakaya, S. Costea, A. Podolnik, and S. Markidis, "Optimizing bit1, a particle-in-cell monte carlo code, with openmp/openacc and gpu acceleration," in International Conference on Computational Science, pp. 316–330, Springer, 2024.
- [20] S. Snyder and et al., "Modular hpc i/o characterization with darshan," in 2016 5th workshop on extreme-scale programming tools (ESPT), pp. 9–17, IEEE, 2016.
- [21] IOR, "Runtime command line options," 2022. Available at: https://ior. readthedocs.io/en/latest/userDoc/options.html#command-line-options (updated: 2022-11-22).
- [22] T. K. Petersen and J. Fragalla, "Optimizing performance of hpc storage systems," in 2013 IEEE High Performance Extreme Computing Conference, Waltham, MA USA, 2013.
- [23] P. Carns, R. Latham, R. Ross, K. Iskra, S. Lang, and K. Riley, "24/7 characterization of petascale i/o workloads," in 2009 IEEE International Conference on Cluster Computing and Workshops, pp. 1–10, IEEE, 2009.
- [24] J. Logan, M. Ainsworth, C. Atkins, J. Chen, J. Y. Choi, J. Gu, J. M. Kress, G. Eisenhauer, B. Geveci, W. Godoy, et al., "Extending the publish/subscribe abstraction for high-performance i/o and data management at extreme scale," Bulletin of the IEEE Technical Committee on Data Engineering, vol. 43, no. 1, 2020.
- [25] W. F. Godoy, N. Podhorszki, R. Wang, C. Atkins, G. Eisenhauer, J. Gu, P. Davis, J. Choi, K. Germaschewski, K. Huck, et al., "Adios 2: The adaptable input output system. a framework for high-performance data management," SoftwareX, vol. 12, p. 100561, 2020.
- [26] K.-W. Lin, S. Byna, J. Chou, and K. Wu, "Optimizing fastquery performance on lustre file system," in Proceedings of the 25th International Conference on Scientific and Statistical Database Management, pp. 1–12, 2013.
- [27] W. Yu, J. S. Vetter, and H. S. Oral, "Performance characterization and optimization of parallel i/o on the cray xt," in 2008 IEEE International Symposium on Parallel and Distributed Processing, pp. 1–11, IEEE, 2008.
- [28] S. Markidis, D. Gadioli, E. Vitali, and G. Palermo, "Understanding the i/o impact on the performance of high-throughput molecular docking," in 2021 IEEE/ACM Sixth International Parallel Data Systems Workshop (PDSW), pp. 9–14, IEEE, 2021.
- [29] S. Saini, J. Rappleye, J. Chang, D. Barker, P. Mehrotra, and R. Biswas, "I/o performance characterization of lustre and nasa applications on pleiades," in 2012 19th International Conference on High Performance Computing, pp. 1–10, IEEE, 2012.
- [30] L. Wan, A. Huebl, J. Gu, F. Poeschel, A. Gainaru, R. Wang, J. Chen, X. Liang, D. Ganyushin, T. Munson, et al., "Improving i/o performance for exascale applications through online data layout reorganization," IEEE Transactions on Parallel and Distributed Systems, vol. 33, no. 4, pp. 878–890, 2021.
- [31] A. Huebl, R. Widera, F. Schmitt, A. Matthes, N. Podhorszki, J. Y. Choi, S. Klasky, and M. Bussmann, "On the scalability of data reduction techniques in current and upcoming hpc systems from an application perspective," in International Conference on High Performance Computing, pp. 15–29, Springer, 2017.
- [32] T. Banerjee, J. Choi, J. Lee, Q. Gong, R. Wang, S. Klasky, A. Rangarajan, and S. Ranka, "An algorithmic and software pipeline for very large scale scientific data compression with error guarantees," in 2022 IEEE 29th International Conference on High Performance Computing, Data, and Analytics (HiPC), pp. 226–235, IEEE, 2022.
- [33] J. Gu, P. Davis, G. Eisenhauer, W. Godoy, A. Huebl, S. Klasky, M. Parashar, N. Podhorszki, F. Poeschel, J. Vay, et al., "Organizing large data sets for efficient analyses on hpc systems," in Journal of Physics: Conference Series, vol. 2224, p. 012042, IOP Publishing, 2022.
- [34] T. W. Crockett, "File concepts for parallel i/o," in Proceedings of the 1989 ACM/IEEE conference on Supercomputing, pp. 574–579, 1989.
- [35] D. V. James, A. T. Laundrie, S. Gjessing, and G. S. Sohi, "Distributeddirectory scheme: Scalable coherent interface," Computer, vol. 23, no. 6, pp. 74–77, 1990.
- [36] C. K. Birdsall and A. B. Langdon, Plasma physics via computer simulation. CRC press, 2018.
- [37] C. K. Birdsall, "Particle-in-Cell charged-particle simulations, plus Monte Carlo collisions with neutral atoms, PIC-MCC," IEEE Transactions on plasma science, vol. 19, no. 2, pp. 65–85, 1991.

