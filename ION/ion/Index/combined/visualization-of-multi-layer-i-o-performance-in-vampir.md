# Visualization of Multi-layer I/O Performance in Vampir

Hartmut Mix, Christian Herold, and Matthias Weber

*Center for Information Services and High Performance Computing Technische Universitat Dresden, Germany* ¨ {*hartmut.mix, christian.herold, matthias.weber*}*@tu-dresden.de*

*Abstract*—Nowadays, high performance computing systems provide a wide range of storage technologies like HDDs, SSDs or network devices. With the introduction of NVRAM, these systems become more heterogenous and finally provide a complex I/O stack that is challenging to use for applications. However, parallel programs have to efficiently utilize available I/O resources to overcome the scalability problem. Typically, performance analysis tools focus on investigating computation efficiency, executed program paths, and communication patterns. However, these tools only visualize I/O performance information of single layers of the I/O stack. To fully understand the I/O behavior of an application, it is necessary to investigate the interaction between the layers.

This work introduces new visualizations of I/O performance events and metrics throughout the complete I/O stack of parallel applications. We implement our approach on the basis of the performance analysis tool Vampir. We extend its timeline visualizations with performance details of I/O operations. Further, we introduce a new timeline view which depicts I/O activities on each layer of the used I/O stack as well as the interaction between layers. This view enables application developers to identify I/O bottlenecks across layers of a complicated I/O stack. We demonstrate our I/O performance visualization approach with a case study of a cloud model simulation code. Thereby, we analyze the I/O behavior in detail, including information of all involved multi-layered I/O libraries.

# *Keywords*-performance analysis, I/O, tracing, visualization, high performance computing.

## I. INTRODUCTION

Performance analysis and optimization is a key concern in the development of efficient parallel software. Therefore, sophisticated software tools help software developers to analyze and optimize their codes. Parallelization and communication aspects of the HPC applications have been investigated widely for many years.

The computation capabilities of modern systems considerably outperform the capabilities of their I/O subsystems. Thus, the performance of many applications is not limited by the compute power of the CPUs or GPUs, but rather by the available memory or I/O bandwidth. Nevertheless, only a small number of tools support performance analysis application I/O behavior.

Many HPC applications use high-level I/O libraries (e.g., NetCDF [18], HDF5 [17], VTK [14], or ADIOS [10]) for reading and writing of data. These libraries internally use common parallel I/O paradigms like MPI-I/O [11]. This leads to stacked I/O layers. For example NetCDF uses HDF5 internally. HDF5 in turn uses MPI-I/O internally and MPI-I/O uses POSIX-I/O [19] internally. In addition applications may also use multiple I/O paradigms at the same time. Thus, analyzing and optimizing I/O operations on a single layer may not suffice, as interactions between different layers can severely affect the overall performance of the application.

In this paper we present our approach to support the analysis of applications using multi-layer I/O operations. We add visualizations of detailed I/O performance information to the performance analysis tool *Vampir* [12]. Description of the implementation of related internals in the monitoring tool Score-P [1] is not in the scope of this paper. Score-P records I/O performance data during the application run and writes measured data to disk using the OTF2 trace format [6]. OTF2 provides specific event and definition records for I/O activities. We use these records as data basis for our new visualizations. The new version of Vampir tightly integrates I/O events in its timeline representations. Our new visualizations enable the developers to gain detailed insight into the I/O behavior of their applications.

The contributions of this work are:

- Integration of multi-layer I/O information in Vampir displays (*Master Timeline*, *Process Timeline*, and *Performance Radar*).
- A new dedicated timeline view (*I/O Timeline*) for analyzing I/O behavior over time.
- A new configurable and adaptable profile view for I/O operations (*I/O Summary*).
- Extensive filtering capabilities allowing to freely exclude I/O operations from the analysis.
- Implementation of our approach in the performance analysis tool *Vampir*.
- A detailed I/O analysis study of the application MONC.

The remainder of this paper is organized as follows: We review related work and discuss current I/O analysis techniques in Section II. In Section III we describe our visualization approach for multi-layered I/O operations in *Vampir*. We demonstrate the potential of our visualizations with an analysis study in Section IV. Section V concludes this work and lists future work.

## II. RELATED WORK

A wide field of performance analysis tools and techniques exists to support development of highly scalable applications. We base our work on the established performance monitoring and analysis tools Score-P and Vampir.

The measurement infrastructure Score-P [1] records performance metrics of an application. It focuses on analyzing HPC applications, and thus, follows a highly scalable approach. Score-P uses instrumentation or sampling techniques to acquire performance data during the application execution. It stores measured data completely as event logs (trace files) or assembles compact profile reports. Event log data retain all measured information, especially timestamps, and can be considered as a stream of application events. This detailed data provides large potential for identification of performance problems but usually comes at the price of large data volumes. In this work we use the performance data contained in the Open Trace Format 2 (OTF2) [6] event logs of Score-P. Several analysis tools, such as Vampir [12], Scalasca [7], and TAU [15] use Score-P as their default measurement framework.

Vampir [12] is a performance analysis tool that specializes in the visualization of event logs. Vampir reads OTF2 trace files and presents this data in various timeline and profile views. We describe details of Vampir visualizations in Section III. Our contributions extend and build on top of the available functionality of Vampir.

Implementing efficient I/O operations is a performance critical part in the development of parallel applications. The underlying complexity stemming from multiple involved software layers and sophisticated I/O subsystems renders this a challenging task. In spite of its importance, only few tools support developers in performing detailed analyses of application I/O behavior.

Linux distributions usually ship a small set of tools for monitoring or measuring I/O usage. Such tools include *iostat*, *iotop, or blktrace*. *iostat* is part of the *sysstat* collection [16] and reports accumulated device usage metrics. Read and write operations are grouped by block-device. *iotop* monitors and shows I/O operations for each thread individually. *blktrace* is used to analyze I/O accesses. It provides a very detailed look at I/O usage. An additional utility for performance monitoring is the *System Activity Report* (SAR). SAR is also part of the *sysstat* collection. Besides general system metrics, SAR also provides specific information related to I/O devices (e.g., requests issued to physical devices, data blocks read or written). While these Linux tools provide analysis potential for I/O activities of applications, they still focus on system monitoring rather than application optimization. In contrast to our approach these tools are limited to the POSIX-I/O layer.

The profiler Arm MAP [2] can record Lustre performance counters along with application performance data. This enables developers to assess Lustre I/O operations in the context of other application activity.

The I/O characterization tool Darshan [5] records I/O behavior of MPI applications. Darshan's measurements capture all involved software layers. Its scalable and lightweight design allows full-time deployment on large systems. However, Darshan provides only aggregated profile reports. This limits its analysis capabilities for I/O problems with dynamic timing components.

The discontinued research project *Scalable I/O for Extreme Performance* (SIOX) [9] designed a monitoring system with automatic I/O analysis and optimization capabilities. The designed system covered all software and hardware layers involved in individual I/O commands. In comparison to our approach, SIOX provides only coarse-grain measurement accuracy.

## III. METHODOLOGY

In this section we describe our approach for the visualization of I/O behavior of applications. Our visualizations use new I/O event records added to the OTF2 trace format, starting with version 2.1 [13]. We used a prototype version of Score-P to record application I/O activities including the use of NetCDF, MPI-I/O, and POSIX-I/O.

The following sub-sections describe our visualization techniques grouped by individual displays of Vampir [8]. Each display has an own analysis focus and consequently uses different visualization approaches.

## *A. Master Timeline and Process Timeline*

Timeline displays show recorded events on a horizontal time axis. Vampir provides the functionality to zoom into areas of interest to investigate them in more detail. To facilitate comparison between different timelines, Vampir aligns all timeline displays and couples their zoom. The *Master Timeline* and the *Process Timeline* displays show information about function invocations, communication, and synchronization. Both displays allow to investigate these aspects of the application runtime behavior in detail. The

![](_page_1_Figure_15.png)

![](_page_1_Figure_16.png)

Figure 2. Process Timeline display showing the individual call levels of the process Master thread:0 in Figure 1.

Master Timeline shows all recorded processes/threads in one display next to each other, Figure 1. Each row represents one process/thread. The Process Timeline focuses on displaying activities of individual processes/threads, Figure 2. In this display the rows represent individual function call levels. For instance in Figure 2, main (level 1) calls MPI_Init (level 2).

In this work we added I/O activities to both displays. This allows to investigate I/O behavior in the context of other application activities. With embedded I/O information, especially the Master Timeline now provides an overview of the complete application behavior. The user can visually inspect what application regions and call stacks issue I/O operations. In detail we show which processes issue I/O operations at which time.

To visualize I/O behavior we indicate the beginning of an I/O operation with a small yellow triangular icon on the initiating process, see Figures 1 and 2. Individual operations are selectable by clicking its icon. This reveals a second triangle connected to the selected triangle. Both triangles visually indicate the duration of the selected I/O operation (selected triangle the beginning of the operation, second triangle end of the operation). Moreover, the *Context View*, Figure 3, of Vampir provides additional information about the selected operation. This information includes the number of transferred bytes or I/O file names and file handles of this operation.

![](_page_2_Figure_3.png)

Figure 3. Context View showing information about a selected I/O operation.

To maintain visual scalability, we combine dense I/O activities (very many at a very short time) into one graphical "I/O burst" representation. Similar to individual I/O operations, we visualize I/O bursts with yellow triangle icons. Users can distinguish individual I/O operations from I/O bursts by looking for a small black dot in the center of the icon. Only individual I/O operation icons show that small dot. To help users to visually assess the I/O behavior, we encode the number of aggregated activities into the size of I/O burst icons. The more activities aggregated, the bigger the I/O burst icon. Zooming into areas with I/O bursts will show them in more detail and will eventually reveal all corresponding individual I/O operations.

Users can freely change the default color (yellow) of I/O icons. For instance, it is possible to use different colors for individual I/O operations types, like read or write operations. This facilitates visual inspection of individual operations of interest.

## *B. I/O Timeline*

To meet the individual requirements of an I/O analysis we introduce a new timeline display dedicated to this purpose. In contrast to the Master Timeline and Process Timeline, this display focuses on I/O operations. It exclusively displays I/O operations over time and uses their location (e.g. file, handle) as organization criteria. This display is most useful for studying and understanding the I/O behavior over time. It allows to easily find I/O intensive phases of an application and to detect their corresponding I/O intensive locations.

The *I/O Timeline* (Figure 4) provides detailed information of all I/O operation types with respect to their location. Each bar in this timeline presents I/O operations for individual files or file handles, characterized by their file name or handle number, respectively. The display allows to fold sub-timelines into a summarized-timeline. The summarizedtimeline then shows the aggregated I/O operations of all its sub-timelines. This functionality provides the user with visual overviews of the I/O behavior.

The initial setup of the timeline sorts I/O operations in a *File Tree*, shown in Figure 4. This shows at which time during an application's run a certain file is opened, read or written, and closed.

![](_page_2_Figure_12.png)

Figure 4. I/O Timeline showing open and write operations for the file *all-data.txt*.

Unfolding the timeline of a file separates its I/O operations according to their file handles and I/O paradigms. For files we provide additional information about the mount point, the file system type (e.g., Lustre), and their location within the file system, see Figure 5.

![](_page_3_Figure_0.png)

Figure 5. Context View showing detailed information for the file *alldata.txt*.

The second option to sort entries in the I/O Timeline is the *I/O Tree*. This arranges I/O operations and accessed files in relation to the system tree hierarchy. The system tree contains resource information of the target cluster. The hierarchy may span from the complete cluster as root node, over racks and compute nodes, down to individual processing cores running multiple threads. The I/O Tree provides easy visual differentiation between globally and locally mounted files. The top level in the I/O Tree represents the HPC system (e.g., machine Cray XC in Figure 6) and the shared network. The top level includes shared files. Local files, like /dev/null, are assigned to each compute node. File handles for I/O paradigms can be associated with files or handles belonging to different I/O layers. We visualize all I/O operations related to their file handle. Consequently, one and the same file may be listed as both local and global depending on the recorded I/O event.

The *File Tree* and the *I/O Tree* essentially present the same performance information. They merely present a means to organize the information from two different perspectives. Analyzing I/O behavior by looking for operations occurring on individual files is done with the *File Tree*. Similarity, the *I/O Tree* facilitates analyzing I/O behavior by looking for activities on certain hardware topology levels.

We also allow to display I/O events exclusively for an individual file handle. Figure 7 shows all I/O operations related to the file handle *MPI-IO #0*. Moreover, the I/O Timeline also supports the visualization of asynchronous I/O operations. Users can select individual files and see the activities of all threads that access the respective file concurrently.

#### *C. I/O Summary*

In addition to the timeline views, we also provide a profile view dedicated to I/O operations. The *I/O Summary*, shown in Figure 8, gives detailed statistical information of executed I/O operations. This display provides an overview for quickly assessing the overall I/O behavior. An initial analysis

![](_page_3_Figure_7.png)

Figure 6. I/O Timeline showing open and write operations sorted by the *I/O Tree*.

![](_page_3_Figure_9.png)

Figure 7. I/O Timeline showing the I/O operations for a single MPI handle.

usually starts with the I/O Summary display. Metrics like *Number of I/O operations* or *Aggregated I/O transaction time/size* coarsely characterize the I/O intensity and I/O performance of an application.

To further facilitate I/O analysis by allowing to focus statistics on chosen areas, the displayed profile values dynamically adjust to the currently selected time (zoom) interval.

Figure 8 depicts an I/O Summary showing the average transaction time of I/O operations performed on each file.

The *I/O Summary* provides a range of analysis metrics for I/O operations:

- Number of I/O operations
- Aggregated I/O transaction size
- Aggregated I/O transaction time
- I/O transaction size
- I/O transaction time
- I/O bandwidth

Besides the average value, the dialog also keeps the minimum and maximum value for each entry.

The *I/O Summary* can group values for all metrics according to their *Transaction Size*, *File Name*, *Operation Type*, and *Handle*. If I/O libraries are recorded, we separate all events according to their paradigm or layer in the I/O operation hierarchy. We support the following I/O paradigms:

- ISO C I/O
- POSIX I/O
- MPI-I/O
- NetCDF

Users can restrict the computed profile values to specific I/O operation types. Available options are *Read*, *Sync*, *Write*,

|  | All Processes, Average I/O Transaction Time per File Name for POSIX I/O |  |  |
| --- | --- | --- | --- |
| 3 ms | 2 ms 1 ms |  | 0 ms |
| 3.316 ms |  |  | /fs2/d131/d131/sha...mples/all-data.txt |
|  |  |  | 27.989 us /dev/xpmem |
|  |  |  | 21.465 us /dev/null |
|  |  |  | 21.286 us /dev/shm/crav-sha...9830327-16857.tmp |
|  |  |  | 20.321 us //dev/shm/cray-sha ... 327-1-1-16857.tmp |
|  |  |  | 13.67 us /dev/shm/cray-sha ... 327-2-2-16857.tmp |
|  |  |  | 7.444 µs | /var/opt/cray/alps ... ool/places29830327 |
|  |  | 5.796 us Other |  |

Figure 8. I/O Summary chart showing the average transaction time of I/O operations performed on the POSIX-I/O layer.

*All Data* operations. Additionally, it is possible to directly select the operation types using the I/O filter dialog, explained in Section III-E.

## *D. File I/O Metrics*

To further facilitate characterization of an application's I/O behavior, we provide visualizations of performance counters. For instance, users can visualize Lustre file system metrics recorded via the PAPI counter interface [4]. Vampir provides the *Performance Radar* (not shown) and *Counter Data Timeline* (Figure 9) displays for investigating the progress of counter values over time.

Besides the analysis of function calls, the visualization of performance counter recordings adds an new dimension of performance data to the analysis. For instance, performance counters allow to visualize the I/O bandwidth or the amount of transferred data over time. Such information considerably helps to detect bottlenecks and focus the analysis on critical sections of an application.

![](_page_4_Figure_6.png)

Figure 9. Counter Timeline showing the *I/O Volume in Transit* for one process.

Next to recorded counter values, we provide a set of predefined and customizable metrics. Vampir computes these metrics internally using the trace data. For the analysis of I/O behavior we designed the following metrics:

- *I/O Bandwidth*: Aggregated file I/O bandwidth
- *I/O Volume in Transit*: Aggregated number of bytes in transit to and from the I/O system
- *Simultaneous I/O Operations*: Number of interleaved I/O directives

The *Custom Metrics Editor* (not shown) allows to define own derived metrics based on existing counters and functions. For instance, our I/O metrics can be restricted to certain I/O paradigms, I/O types or a set of file names.

## *E. I/O Filter*

![](_page_4_Figure_14.png)

Figure 10. I/O filter dialog for selecting visualized I/O information.

We provide the new *I/O Filter* to enable users to tailor the visualized I/O information exactly to their analysis needs. Figure 10 shows the *I/O Events Filter* dialog. This dialog provides various filter criteria based on I/O paradigm, file name, file handle, operation type, and operation flag. Available paradigms, files, or handles are organized in a tree-based presentation, similar to the tree view of the I/O Timeline.

#### IV. CASE STUDY

As an example application to showcase the value of this work, we did a performance study of the Met Office NERC Cloud model (MONC) code [3]. MONC is a complete re-write of the UK Met Office Large Eddy Model (LEM) simulation and written in Fortran 2003. It uses MPI for parallelism and NetCDF to store results on disk. The MONC application consists of two sets of processes running simultaneously. Simulation processes (or computation processes) produce raw (prognostic) results. Separate I/O server processes are dedicated to handling and analyzing the data produced by the model. The I/O server receives the raw simulation results in irregular intervals, performs data analytics to produce meaningful (diagnostic) results and then stores this on disk. MONC allows users to configure the number of I/O server processes. Much of the data analytics involves combining local values to form final results, therefore the program is more communication and I/O bound rather than being computation bound [3].

All the experiments were executed on a Cray XC30, running on 1 to 4 nodes containing two 2.7 GHz, 12 core Intel Xeon E5-2697 v2 (Ivy Bridge) series processors. We instrumented the MONC application with Score-P by modifying the build process. During the measurement, Score-P intercepts library calls to NetCDF, MPI as well as POSIX. The resulting performance events and metrics are stored in an OTF2 archive. We analyzed and visualized this trace with the Vampir prototype that contains the developed methodologies from Section III.

![](_page_5_Figure_0.png)

Figure 11. Trace visualization in Vampir containing our I/O extensions in the Master Timeline and I/O Timeline charts. The Function Summary charts at the right side give an overview of the application behavior.

Figure 11 depicts the visualization of the MONC trace file and provides an overview of the application behavior. The function summaries on the right depict the accumulated time per function group for the I/O server (top chart) and simulation (bottom chart) processes. The chart top right shows that I/O server processes spent most time in Pthread functions and only little time in I/O routines. As expected, simulation processes (bottom chart) perform also less I/O operations and spent most time in application code. As an early result, the summaries expose that the recorded MONC case exhibits only few I/O activities. Further analyses will now investigate the details of MONC I/O characteristics. Figure 11 also depicts the Master Timeline view at the top left which visualizes different program phases as well as their distinctive I/O behavior for the first 12 processes. The first yellow triangles depict the initialization phase which reads configuration data on all processes. Afterwards, multiple black circles visualize intense communication between the MPI processes which arises during the computation of simulation results. Furthermore, green boxes represent the computation functions of the simulation phase. Red boxes indicating MPI *Finalize* calls depict the finalization phase on the simulation processes. On the I/O server processes, this phase is characteristic for performing many I/O operations (yellow triangles) to store the results. Hereby, the I/O server processes delay the program finalization and force the simulation processes to wait until the I/O activities are finished.

In order to find the reason of the delay, Figure 12 depicts the timelines of each I/O server thread for *MPI Rank 6*. The timeline of *Pthread thread 8:6* shows the yellow triangles for the I/O operations, and the MPI operations (red boxes) and POSIX-I/O routines (yellow boxes). Only two threads are utilized while the other ones are pending and waiting on I/O requests from the master thread. For this configuration of MONC, the number of threads can be limited to 2. This chart also shows a crucial I/O behavior with thread 8 only performing I/O operations after thread 7 has finished. As a consequence, there are no concurrent I/O accesses within the I/O servers. This is probably due to NetCDF not being thread-safe.

To understand the I/O behavior of NetCDF, Figure 13 depicts the Process Timeline of the 8th thread of process 6. The chart shows the NetCDF function nc put *var1 long*

![](_page_6_Figure_0.png)

Figure 12. Extract from the Master Timeline showing the write operations on the *Pthread thread 8:6* and *Pthread thread 7:6* of MPI Rank 6.

![](_page_6_Figure_2.png)

Figure 13. Call stack of a NetCDF write operation on a single I/O process.

(orange box) in call level 8 which internally calls the MPI-I/O function MPI *File write* at (red box) in level 9. Finally, the MPI-I/O routine calls the POSIX-IO *lseek* and *write* operations (yellow boxes) in level 10. Also the I/O Timeline view in Figure 14 visualizes this operation sequence but includes the file and file handle context. The write operations of the POSIX-I/O handle #21 relate to the MPI-I/O handle #0, and this again to the NetCDF file handle #0 for the NetCDF file RCE *dump2 18.nc*. Additionally, a number of write operations to other small local files like map-files are involved in the MPI-I/O operation as well. The statistical analysis of the I/O operations (not shown) results in a large number of very small write operations in contrast to only a few write operations that transfer a large number of bytes (in the order of mega- or gigabytes) per operation. Yet, as Figure 15 depicts, the aggregated time spent for all these involved small write operations at all processes is in the same order of magnitude as the time spent for the larger write operations. In the displayed time slice, the accumulated time of MPI write operations is 46.7 seconds for large data transfers (about 18.5 Mbytes per operation). Interestingly, the aggregated time of small MPI-I/O operations writing only 8 bytes is also 43.3 seconds.

This detailed visualization presents a good starting point for further performance optimizations of this application. Particularly useful is the possibility to analyze the inter-

![](_page_6_Figure_6.png)

Figure 14. Detail of the I/O Timeline display showing the write operations for the NetCDF file in the *File Tree* representation.

![](_page_6_Figure_8.png)

Figure 15. Aggregated MPI-I/O transaction time in dependency of the amount of transferred bytes per operation.

nal implementation of the I/O operations by the used I/O libraries, which was totally hidden in previous performance analysis studies so far.

## V. CONCLUSIONS AND FUTURE WORK

Many HPC applications exhibit complex I/O characteristics, including the use of multi-layered libraries and parallel file systems. Therefore, software developers require capable analysis tools that visualize I/O operations in detail and full complexity.

Our work adds I/O analysis capabilities to the performance analysis tool *Vampir*. We provide powerful visualizations that show I/O behavior in detail. Our contributions enable developers to identify performance bottlenecks caused by inefficient I/O operations. Further, our approach allows to pinpoint performance problems caused by the interplay between multiple I/O layers.

Starting with version 9.4, all presented functionality is included in the official *Vampir* software releases.

In the future we plan to extend our analysis methods by correlating performance counter readings (e.g., Lustre counters) with their respective function call invocations. This will help developers to assess the I/O performance characteristics of individual code sections. Additionally, we plan to add analysis support for NVRAM hardware.

## ACKNOWLEDGMENT

The authors would like to thank all developers and testers of the software tools *Score-P* and *Vampir* that made this work possible.

Parts of this research were undertaken in the context of the NEXTGenIO project, which is funded through the European Union's Horizon 2020 Research and Innovation programme under Grant Agreement no. 671951.

## REFERENCES

- [1] D. an Mey, S. Biersdorf, C. Bischof, K. Diethelm, D. Eschweiler, M. Gerndt, A. Knupfer, D. Lorenz, A. Malony, ¨ W. E. Nagel, et al. Score-P: A unified performance measurement system for petascale applications. In *Competence in High Performance Computing 2010*, pages 85–97. Springer, 2012.
- [2] Arm Forge (Arm MAP) Version 18.0. https://www.arm.com/ products/development-tools/hpc-tools/cross-platform/forge, Feb. 2018.
- [3] N. Brown, M. Weiland, A. Hill, M. Geimer, B. Shipway, C. Maynard, T. Allen, and M. Rezny. A highly scalable Met Office NERC Cloud model. In *Proceedings of the 3rd International Conference on Exascale Applications and Software (EASC '15)*, pages 132–137, Scotland, UK, 2015. University of Edinburgh.
- [4] S. Browne, J. Dongarra, N. Garner, G. Ho, and P. Mucci. A portable programming interface for performance evaluation on modern processors. *International Journal of High Performance Computing Applications*, 14(3):189–204, 2000.
- [5] P. Carns, K. Harms, W. Allcock, C. Bacon, S. Lang, R. Latham, and R. Ross. Understanding and improving computational science storage access through continuous characterization. *Trans. Storage*, 7(3):8:1–8:26, Oct. 2011.
- [6] D. Eschweiler, M. Wagner, M. Geimer, A. Knupfer, W. E. ¨ Nagel, and F. Wolf. Open Trace Format 2: The Next Generation of Scalable Trace Formats and Support Libraries. In *Applications, Tools and Techniques on the Road to Exascale Computing*, volume 22 of *Advances in Parallel Computing*, pages 481 – 490, 2012.
- [7] M. Geimer, F. Wolf, B. J. N. Wylie, E. Abrah ´ am, D. Becker, ´ and B. Mohr. The Scalasca Performance Toolset Architecture. *Concurr. Comput. : Pract. Exper.*, 22(6):702–719, Apr. 2010.
- [8] GWT-TUD GmbH. Vampir 9 User Manual, Version Vampir 9.4. https://www.vampir.eu/public/files/pdf/manual.pdf, Nov. 2017.
- [9] J. Kunkel, N. Hubbe, A. Aguilera, H. Mickler, X. Wang, ¨ A. Chut, T. Bonisch, J. L ¨ uttgau, R. Michel, and J. Weging. ¨ The SIOX Architecture Coupling Automatic Monitoring and Optimization of Parallel I/O. *Supercomputing*, page 245260, 2014.

- [10] Q. Liu, J. Logan, Y. Tian, H. Abbasi, N. Podhorszki, J. Y. Choi, S. Klasky, R. Tchoua, J. Lofstead, R. Oldfield, M. Parashar, N. Samatova, K. Schwan, A. Shoshani, M. Wolf, K. Wu, and W. Yu. Hello ADIOS: the challenges and lessons of developing leadership class I/O frameworks. *Concurrency and Computation: Practice and Experience*, 26(7):1453– 1473, 2014.
- [11] Message Passing Interface Forum. MPI: A Message-Passing Interface Standard, Version 3.1. http://www.mpi-forum.org/ docs/mpi-3.1/mpi31-report.pdf, June 2015.
- [12] M. S. Muller, A. Kn ¨ upfer, M. Jurenz, M. Lieber, H. Brunst, ¨ H. Mix, and W. E. Nagel. Developing Scalable Applications with Vampir, VampirServer and VampirTrace. In C. Bischof, M. Bucker, P. Gibbon, G. R. Joubert, T. Lippert, B. Mohr, ¨ and F. J. Peters, editors, *Parallel Computing: Architectures, Algorithms and Applications*, volume 15 of *Advances in Parallel Computing*, pages 637–644. IOS Press, 2008.
- [13] Open Trace Format 2 User Manual, Version 2.1. https://silc. zih.tu-dresden.de/otf2-2.1.pdf, Feb. 2018.
- [14] W. Schroeder, K. Martin, and B. Lorensen. *The Visualization Toolkit (4th ed.)*. Kitware, 2006.
- [15] S. S. Shende and A. D. Malony. The Tau Parallel Performance System. *Int. J. High Perform. Comput. Appl.*, 20(2):287–311, 2006.
- [16] SYSSTAT Utilities Homepage. http://sebastien.godard. pagesperso-orange.fr, Feb. 2018.
- [17] The HDF Group. HDF5 Software Documentation. https: //support.hdfgroup.org/HDF5/doc/index.html, Feb. 2018.
- [18] Unidata a member of the UCAR Community Programs. Network Common Data Form (NetCDF). https://www.unidata. ucar.edu/software/netcdf/, Feb. 2018.
- [19] M. Vilayannur, S. Lang, R. Ross, R. Klundt, L. Ward, Mathematics, I. Computer Science, VMWare, and SNL. *Extending the POSIX I/O Interface: A Parallel File System Perspective*. Argonne National Laboratory, Dec 2008.

