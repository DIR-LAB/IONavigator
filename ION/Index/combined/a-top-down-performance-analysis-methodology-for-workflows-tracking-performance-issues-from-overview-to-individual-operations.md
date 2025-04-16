# A Top-Down Performance Analysis Methodology for Workflows: Tracking Performance Issues from Overview to Individual Operations

Ronny Tschuter, Christian Herold, William Williams, ¨ Maximilian Knespel, Matthias Weber Technische Universitat Dresden ¨ ronny.tschueter@tu-dresden.de, christian.herold@tu-dresden.de, william.williams@mailbox.tu-dresden.de, maximilian.knespel@tu-dresden.de, matthias.weber@tu-dresden.de

*Abstract*—Scientific workflows are well established in parallel computing. A workflow represents a conceptual description of work items and their dependencies. Researchers can use workflows to abstract away implementation details or resources to focus on the high-level behavior of their work items. Due to these abstractions and the complexity of scientific workflows, finding performance bottlenecks along with their root causes can quickly become involving. This work presents a top-down methodology for performance analysis of workflows to support users in this challenging task. Our work provides summarized performance metrics covering different workflow perspectives, from general overview to individual jobs and their job steps. These summaries allow to identify inefficiencies and determine the responsible job steps. In addition, we record detailed performance data about job steps, enabling a fine-grained analysis of the associated execution to exactly pinpoint performance issues. The introduced methodology provides a powerful tool for comprehensive performance analysis of complex workflows.

*Index Terms*—scientific workflows, job scheduling, data dependencies, I/O, performance analysis, profiling, tracing

# I. INTRODUCTION

Today, scientists face the challenge of data-intensive computing on parallel and distributed platforms. Current experiments such as LIGO [1] and LHC [2] produce data volumes that cannot be handled by a single computing system. Data analysis and interpretation also requires collaboration among scientists from various domains. Scientific workflows have been established for this task [3]. Workflow management systems (WMS) support scientists in systematically describing tasks, expressing dependencies between tasks, allocating compute resources to execute tasks, and managing data.

In this work, we consider a workflow as a coordinated sequence of interdependent applications. A *Workflow* can be modeled as *Jobs* composed of *Job Steps*. Each Job represents a single submission to the scheduling system, and each Job *Step* executes a single application. Figure 1 illustrates an example of a workflow with three individual jobs. *Jobs* may be dependent on each other. Therefore, inefficiencies in one *Job Step* not only cause delays in the affected *Job Step* but also propagate to depending *Job Steps*. This results in an increase of the overall workflow runtime. Identifying a bottleneck in a complex workflow is a challenging task without

![](_page_0_Figure_8.png)

Fig. 1: A *Workflow* example containing three *Jobs*. The *Job Steps* represent command executions, e.g., mpirun.

tool support. Optimization of the *Job Step* or application responsible for the bottleneck requires detailed information about its runtime behavior. According to Shneiderman's Visual Information Seeking Mantra [4], we propose a top-down approach that scales the performance data from a global (the entire workflow) to a detailed (application level) view.

In order to implement our approach, we developed/extended the following tools: JobLog, recording job information such as dependencies; OTF2-Profile, generating profiles from OTF2 traces; and Workflow Visualizer, processing and visualizing the performance information of the recorded workflow.

Our contributions in this paper include:

- designing and implementing a top-down approach for workflow performance analysis,
- adding a new JSON output format to OTF2-Profile,
- providing a tool to query and incorporate job scheduling information,
- implementing a GUI to facilitate performance analysis of scientific workflows, and
- integrating our approach in an existing WMS infrastructure with customized wrapper scripts.

The remainder of this paper is organized as follows. Section II provides background information and puts our work in context. In Section III, we detail the methodology of our top-down approach. Section IV describes the implementation and gives an overview of the tools involved. In Section V, we demonstrate our approach in case studies. Section VI presents concluding remarks and gives an outlook on future work.

# II. RELATED WORK

Our work relates to Workflow Management Systems, batch systems, and performance analysis.

*a) Workflow Management Systems:* A Workflow Management System (WMS) coordinates data processing and supports collaboration of researchers using distributed systems in order to achieve a common goal or task [5]. Workflow Management Systems are established in grid and cloud domains, but they are also more and more commonly used on traditional clusters and High Performance Computing (HPC) systems. Examples of widely used scientific workflow systems are Apache Airavata [6], Apache Taverna [7], Kepler [8], and Pegasus [9], [10].

A WMS has to balance conflicting requirements. On the one hand, scientists pose high demands on the usability of a WMS. On the other hand, a WMS has to ensure efficient resource utilization. Especially for the latter request, performance monitoring is an essential task. As workflows are a complex composition of individual tasks, analysis of a single application is generally insufficient. Users demand options to monitor and steer entire workflows [11]. Costa et al. [12] present an online approach for workflow monitoring and tuning. Their monitoring tracks provenance data, which they define as dependencies between data sets. They store this provenance information in a database that allows queries during the workflow execution. Yoo et al. [13] include system logs and application performance statistics in their WMS monitoring. Krol et al. [14] base their workflow analysis on ´ performance profiles. They collect metrics in equidistant points in time during a workflow run and combine data from multiple executions of the same workflow configuration.

Deelman et al. [15] identified the interactions of Workflow Management Systems and the software ecosystem of HPC platforms as a major field of research in their study about the future of scientific workflows on extreme-scale computing systems. We address this field of research by introducing a methodology for performance analysis and optimization of entire scientific workflows as well as individual jobs and job steps forming the workflow. Although this work focuses on workflow executions on HPC systems, the presented methodology is not limited to this specific application domain.

Da Silva et al. [16] propose a dynamic provenance capture concept providing different levels of detail to users. They suggest to start with collecting provenance data at a coarse information level. If (performance) problems are detected in the workflow execution, they suggest to switch to a more detailed recording mode. Our work follows this idea and provides a performance analysis toolchain according to their proposal.

Current research [17], [18] simulates workflows and Workflow Management Systems to investigate scheduling techniques or predict performance metrics of a workflow. These studies require a precise characterization of the workflow's workload. Because the methodology presented in this paper records this information, results of our work can be used to parameterize WMS simulations.

![](_page_1_Figure_7.png)

Fig. 2: The top-down workflow analysis approach follows the hierarchical structure of workflows. The top level provides a general overview of the entire *Workflow*. Subsequent levels add more detailed information for the individual workflow parts.

*b) Batch Systems:* Because multiple users usually share the resources of an HPC system, batch systems are required to manage resource allocation and control program execution. Batch systems such as Slurm Workload Manager [19], Portable Batch System (PBS) [20], or Platform Load Sharing Facility (LSF) [21] support users in defining workflows, expressing job dependencies, submitting jobs, and monitoring their execution.

In this work we record batch system information like job dependencies, job start and end times, or job queuing time to provide a comprehensive workflow analysis.

*c) Application Performance Analysis:* Performance analysis has a long tradition in the field of HPC, with a wide range of established tools. Some members of this group, such as TAU [22] and HPCToolkit [23], focus on profiling of parallel applications and present statistics about runtime and resource utilization. These statistics can help users to identify frequently called functions or discover parts of an application that consume a considerable amount of runtime.

In contrast, monitoring tools such as Score-P [24], collect detailed event logs (traces) of an application execution. Analysis tools such as Vampir [25] provide intuitive timeline visualizations of trace data and reveal dynamic effects in the application behavior, e.g., performance issues that evolve during execution.

Our work combines both approaches by presenting event logs for individual job steps and derived statistics for the workflow levels.

McCraken et al. [26] state that traditional HPC performance analysis tools highly focus on computational performance, neglecting other productivity bottlenecks such as queue waiting times, storage capacities, and data transfer speeds. With this work, we try to widen the scope of performance analysis by combining information from all levels of scientific workflows.

## III. METHODOLOGY

In this section we introduce our methodology for performance analysis of workflows and provide a conceptual overview.

Our approach follows the classical visual information seeking mantra in form of a top-down workflow analysis procedure. As illustrated in Figure 2, the analysis starts with an overview of the entire workflow and then proceeds down the hierarchical structure of workloads, thereby increasing analysis detail. Figure 3 depicts the typical workflow structure with an example *Workflow* consisting of two *Jobs*, containing two *Job Steps* each. Our approach provides relevant performance information at a suitable level of detail for each level of the workflow. Users start their analyses with an overview of the entire workflow structure. Aggregated performance metrics support this initial analysis view. The presented information guides users to problematic *Jobs*. Upon selecting a Job, our approach adds detailed performance information precisely characterizing the Job. This ultimately allows users to identify the performance critical parts of the workflow. Finally, users examine individual *Job Steps* of the selected Job to reveal the root cause of any performance issues detected. We support this last analysis step by providing fully detailed trace data for Job *Steps*.

Next, we describe the workflow analysis procedure in detail by following the individual analysis levels.

# *A. Workflow Level*

This initial level provides performance summaries of all *Jobs* and provides a general overview of the entire *Workflow*. A visualization of the workflow execution structure shows dependencies between *Jobs* and reveals inefficiencies and unused parallelization potential. Additional runtime statistics (*profiles*) categorize workflow time into three groups: *computation*, *communication*, and I/O. This initial analysis facilitates diagnosis of performance problems within the workflow, localizing affected *Jobs* and *Job Steps*, and assessing general performance characteristics. For instance, users can determine whether a workflow is communication bound or if particular *Jobs* dominate the workflow's time to completion. Further, users can estimate the impact of performance problems on the entire workflow. We detail on the implementation of the *Workflow* analysis level in Section IV-C. If an user identifies a particular job that appears to contain a performance issue, he selects this Job and progresses to the next analysis level, the Job Level.

![](_page_2_Figure_4.png)

Fig. 3: Typical hierarchical structure of a workflow.

# *B. Job Level*

At the Job level our approach provides statistics about a specific Job and its *Job Steps*. In comparison to the overall *Workflow* level statistics, the Job level statistics exclusively describe individual *Jobs* and their *Job Steps*. The categorization of metrics into the groups *computation*, *communication/synchronization*, and I/O assists users in assessing the general performance characteristics of selected *Jobs* and their *Job Steps*. Using *Job Step* statistics, we generate summaries about the total *Runtime Share* of a Job. Consequently, these summaries inform users about how individual *Job Steps* and function categories contribute to the overall execution time of a Job. Additionally, we provide an overview of accessed I/O resources. We discuss the tools used to generate these statistics in Section IV-B. At this level, users can identify the most time consuming *Job Steps* or function categories and select individual *Job Steps* for further analysis in the next analysis level, the *Job Step* level.

#### *C. Job Step Level*

This level provides the most detailed performance information, captured in form of event logs or *traces*. Traces represent the chronological series of events occurring during an application's execution. Figure 4 depicts the general structure of trace information. Statistics at the level of individual events, like function calls or communication operations, are available. Users can fully customize the type of recorded events by adjusting the measurement process. For example, users can decide to record function calls, parallelization constructs, or calls to I/O routines. Consequently, this most detailed level provides an outline about the computation, communication, and I/O behavior of a specific *Job Step*. One benefit of complete tracing records is that they preserve full temporal application behavior. In addition to statistics, timeline views allow users to ultimately pinpoint root causes of performance bottlenecks, such as inefficiencies in inter-process communication or synchronization. Section IV-A presents more details on the implementation of performance monitoring at the Job *Step* level.

|  | Time P r o c e s s | O p e r a t i o n |  | P r o c e s s 1 |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| . . . |  |  |  |  |  |  |
| 21 | 1 | ENTER main |  |  | O p e r a t i o n C a l l s Time |  |
| 42 | 2 | ENTER main |  | main | 1 | 78 |
| 55 | 2 | ENTER myFunc |  | myCalc | 2 | 21 |
| 58 | 1 | ENTER myCalc |  |  |  |  |
| 68 | 1 | EXIT | myCalc |  |  |  |
| 75 | 2 | EXIT | myFunc | P r o c e s s 2 |  |  |
| 80 | 2 | EXIT | main |  |  |  |
| 87 | 1 | ENTER myCalc |  |  | O p e r a t i o n C a l l s Time |  |
| 98 | 1 | EXIT | myCalc | main | 1 | 38 |
| 99 | 1 | EXIT | main | myFunc | 1 | 20 |
| . . . |  |  |  | . . . |  |  |

#### (a) Application trace (b) Application profile

Fig. 4: Example of an application trace along with its corresponding profile representation.

![](_page_3_Figure_0.png)

Fig. 5: The workflow measurement infrastructure showing interactions between individual tools.

#### IV. IMPLEMENTATION

In this section we focus on the implementation of the top-down methodology presented in Section III. We discuss details at the *Job Step* (Section IV-A), Job (Section IV-B), and *Workflow* level (Section IV-C).

Recording of fully detailed trace data at the *Job Step* level is an important aspect of our methodology, as it builds the performance data basis for the entire analysis. As opposed to the actual analysis procedure, the processing and preparation of performance data works bottom-up internally. Summarized metrics and performance information are always derived from the data directly at the level below. Therefore, we initially present details about data acquisition and implementation at the *Job Step* level and continue with increasing abstractions towards the *Workflow* level.

Our methodology combines several independent tools that acquire and process all required performance data at the different analysis levels. Figure 5 serves as a visual guideline and illustrates the overall design of our methodology using the example shown in Figure 3.

#### *A. Job Step Level*

The actual performance measurements are conducted at the *Job Step* level. We use the Score-P [24] measurement infrastructure to collect performance data for *Job Steps*. As indicated in Figure 5, we first instrument each *Job Step* using Score-P which monitors the execution of a *Job Step* and collects detailed performance data. The measured data is stored as event log in the Open Trace Format Version 2 (OTF2) [27]. The use of a standardized trace data format allows users to benefit from established trace analysis tools. For instance, Vampir [28] offers a scalable visualization of OTF2 traces and Scalasca [29] provides automatic analyses to detect communication and synchronization inefficiencies.

In a workflow, each *Job Step* produces one trace, e.g., *Job Step A.1* of *Job A* creates *Trace.A.1* in Figure 5. The recorded trace data contains all information necessary to pinpoint performance issues in affected *Job Steps*. Moreover, this detailed data builds the basis for all aggregated statistics at the Job and *Workflow* level.

### *B. Job Level*

To provide a general performance overview of entire *Jobs*, we derive combined statistics from their *Job Step* traces. First, we use the tool OTF2-Profile [30] to generate statistics for each trace file. Then, we aggregate the values for all *Job Steps* that belong to one Job. Section IV-B1 discusses OTF2-Profile in detail.

Besides inspecting performance details, also analyzing dependencies between jobs is an important aspect at the Job level. Relying on performance data alone is insufficient for this purpose. Therefore, we utilize additional sources of information like the scheduling system. In this work, we demonstrate an implementation of our methodology for the Slurm job scheduler, commonly used on HPC systems. In general, it is easy to support additional job schedulers as well by following analog principles. Section IV-B2 describes how we query scheduling information in detail.

*1) OTF2-Profile:* The C++ command-line tool OTF2- Profile reads OTF/OTF2 trace files and generates statistics out of the trace information. OTF2-Profile processes traces in parallel to accommodate large file sizes. This parallel execution feature allows OTF2-Profile to run in a post-processing step, reusing allocated workflow resources.

Figure 5 illustrates OTF2-Profile reading recorded traces and generating corresponding profiles, see *Profile.A.1*, *Profile.A.2*, *Profile.B.1*, and *Profile.B.2* in the figure. Prior to this work, OTF2-Profile stored profiles in the Cube data format for Scalasca and other compatible tools. In this work, we extended OTF2-Profile by a new high-level JSON output format. The JSON output consists of four main components: metadata about the monitored job, a breakdown of the job's runtime share, a summary of function call information, and a summary of I/O handles accessed by the job. In comparison TABLE I: Job metrics queried from the scheduling system.

| Field | Description |
| --- | --- |
| JobId | Job identifier |
| JobName | Name of the job |
| StartTime | Time the job starts running |
| EndTime | Time the job terminates |
| SubmitTime | Time of the job submission |
| NumNodes | Number of allocated nodes |
| NumCPUs | Number of allocated CPUs |
| NumTasks | Number of running tasks |
| Dependency | A list of jobs referenced by ids which must be |
|  | finished before the current job can run |
| ExitCode | Job’s exit code |

to the Cube data format, the JSON output includes additional Job information, such as the job ID, the number of nodes, processes and threads present in the trace, the path to the trace file, and the measurement clock resolution.

The JSON output provides an overview of the I/O, *communication*, and *computation* time share of each *Job Step*. I/O includes all I/O operations recorded in the OTF2 input trace. The OTF2 format natively supports I/O operations of the paradigms ISO C, POSIX, MPI I/O, NetCDF, and HDF5. We provide statistics for each paradigm individually. *Communication* consists of MPI [31] and OpenMP [32] routines. Again, each paradigm is listed separately in the statistics. All remaining CPU time is attributed to one *computation* category. The JSON output additionally lists the serial (only one thread of execution) and parallel (more than one thread or process active) time share of the Job. Currently, we do not distinguish between single-node and multi-node parallelism. An additional I/O handle summary provides a list of accessed files. Each I/O handle entry includes details, such as accessing process, associated I/O paradigms, access modes, and the name of the parent file (for instance POSIX file entries may point to an associated HDF5 parent file). This information allows the reconstruction of data dependencies in subsequent analysis steps.

At the end of the post-processing step, OTF2-Profile produced one JSON profile for each *Job Step*, see Figure 5. During analysis time, the Workflow Visualizer (introduced in Paragraph IV-C1) aggregates *Job Step* profiles to generate summarized Job statistics. This allows users to analyze dependencies between *Jobs* and identify parallelization potential.

*2) JobLog:* In addition to performance data, we also record job scheduling information. This allows to capture the execution order of *Jobs* and their *Job Steps*. Therefore, we implemented a python script, called JobLog [33], that queries job-specific information from an HPC job scheduler. JobLog collects information about a Job after all its *Job Steps* have finished and stores the result in a JSON file. For example in Figure 5, JobLog creates the two job log files Job log A for *Job A* and Job log B for *Job B*. Currently, JobLog only supports the Slurm workload manager. However, it can TABLE II: Job step metrics queried from the scheduling system.

| Field | Description |
| --- | --- |
| JobID | Job step identifier |
| NNodes | Number of nodes allocated for the step |
| NCPUS | Number of CPUs allocated for the step |
| Start | Start time of step |
| End | End time of the step |
| Elapsed | Duration in seconds of the step |
| JobName | Name of the executable |
| NodeList | List of nodes that have been used |
| ExitCode | Exit code of the command |
| State | State of the step |

be easily adapted to other job scheduling systems.

Table I lists the metrics that JobLog queries once for a running job. This information is defined once per job and applies to all *Job Steps* within the job. In contrast, *Job Step* related information is queried for each job step individually. Table II lists this kind of information. It may occur multiple times in one job log file.

At this point, the collected scheduling information along with recorded data dependencies are sufficient to exactly reconstruct the execution of the workflow.

#### *C. Workflow Level*

At the *Workflow* level, we combine all information gathered on other levels and provide an intuitive visualization of the data. Our *Workflow Visualizer* GUI processes the job log files created by JobLog and the JSON profiles created by OTF2- Profile. The GUI guides users through the analysis of their workflows, starting with an overview of the entire workflow, then diving into details by selecting individual jobs and job steps.

*1) Workflow Visualizer:* The graphical user interface Workflow Visualizer allows the user to analyze individual jobs or entire workflows. Depending on that choice, users open a single job log file or a folder that contains all workflow job log and profile data files. Initially, the GUI displays the *Workflow View* main window consisting of *Workflow Graph* (top) and *Info View* (bottom), see Figure 6.

*a) Workflow Graph:* The Workflow Graph depicts jobs, job steps, and accessed files arranged in a graph to visualize job dependencies.

A *Job Box* with an unique background color represents an individual job. Each Job Box is labeled with its corresponding Job <job id>. The upper part of a Job Box contains Job *Step Boxes* for associated job steps. The background coloring of a Job Box indicates the runtime-share of executed function groups. For example, an almost exclusively red-colored Job Box (Job 483507, Step 3) in Figure 7 indicates that this job step spent most of its time in MPI functions. Furthermore, *File Boxes* in the bottom part of the Job Box present informa-

25

![](_page_5_Figure_0.png)

Fig. 6: Workflow Visualizer main window consisting of Workflow Graph (A), Job Summary (B1), Function Runtimes (B2), and Info Table (B3).

![](_page_5_Figure_2.png)

Fig. 7: Zoom to a Job Box in the Workflow Graph. The Info View shows summaries about the selected Job Box.

tion about its I/O operations. There is one box for each access mode (read-only, read/write, write-only; from left to right).

Arrows between jobs illustrate dependencies. Solid arrows represent job dependencies as deduced from the scheduling system. This information is included in the job log files. For example, the job log in Figure 7 lists that Job 483507 depends on Job 483506. Therefore, a solid arrow between both jobs visualizes this dependency. Dashed arrows represent job dependencies derived from job start and end times. Additionally, dashed arrows indicate dependencies based on file access information.

In order to facilitate different analysis goals, the Workflow Graph offers various display modes to arrange Job (Step) Boxes:

- *Dependency Graph*: all Job (Step) Boxes are equally sized and at fixed grid positions, default mode, useful
![](_page_5_Figure_8.png)

Fig. 8: Comparison of the Workflow Graph display modes: Dependency Graph (A), Duration Scaled Dependency Graph (B), Timeline (C).

for dependency analysis (Figure 8 A),

- *Duration Scaled Dependency Graph*: the widths of Job (Step) Boxes are proportional to the duration of jobs/job steps, box positions are similarly to the Dependency Graph display mode with fixed size horizontal gaps, useful to visualize execution time of jobs/job steps while ignoring batch scheduling waiting times (Figure 8 B),
- *Timeline*: scales the widths and positions of Job (Step) Boxes based on their start and end times, horizontal positioning follows a time axis, multiple rows indicate parallel running jobs, useful for performance analysis (Figure 8 C).

*b) Info View:* The bottom charts of Figure 6 show the Info View. This view depicts statistics for the currently selected item. Users can choose statistics about the entire workflow, a job, a job step, or file operations by selecting the respective tab.

Figure 6 illustrates statistics for the workflow (the *Workflow View* tab is active). In this example, the Info View shows runtimes of jobs and function categories as well as scheduling information. In addition to absolute values for runtimes, pie charts visualize their respective share of overall runtime.

The *Job Step View* tab allows the user to open related trace data in Vampir (if available on the system) to visualize the fully detailed event log.

The *File Info* tab lists access information for the currently selected file. Based on file access information, the tool derives dependencies. For example, users can easily determine all jobs which opened a particular file for writing previously, or which will open the file later for reading or writing.

![](_page_6_Figure_0.png)

Fig. 9: Visualization of the synthetic workflow (timeline mode).

![](_page_6_Figure_2.png)

Fig. 10: Performance profiles of Job 45 from Figure 9. Job Step 2 spends significant time in MPI routines.

#### V. CASE STUDY

This section demonstrates our top-down methodology in three case studies. *Synthetic Workflow*, the first case, focuses on analyzing complex workflow structures. In the second case, *GATK / Cromwell*, we highlight the support of workflow management systems. The third case, *GROMACS*, shows the process of tackling performance problems from overview to root cause.

*a) Synthetic Workflow:* This paragraph demonstrates the analysis process with a synthetic workflow. Figure 9 depicts the Workflow Visualizer showing the general structure of the workflow. This synthetic workflow consists of five individual jobs. The workflow starts with Job 42 containing four job steps. The coloring of the Job Step Boxes indicates that almost all job steps are compute intensive. Only Job Step 3 spends about half of its runtime in MPI functions (red color). However, as the runtime of Job 42 is relatively small in comparison to the total runtime of the workflow, we won't instigate this issue any further.

A sequence of parallel jobs starts after the completion of Job 42. Jobs 43 and 45 run in parallel to Job 44. Solid arrows indicate dependencies of Jobs 43 and 44 on Job 42. The Jobs 43, 44, and 45 consist of three job steps, respectively. In all three jobs, the second job step dominates the runtime and shows a significant MPI runtime share (red color). Consequently, these job steps are candidates for further analysis and optimization. Figure 10 shows Job 45 in detail. The *Job Step Info* chart indicates that almost half of the selected Job Step 2 runtime was spent in MPI. Further analysis of the event logs is recommended to identify the root cause of this excessive MPI time. Probably performance critical communication patterns or load imbalances lead to increased MPI wait times.

The workflow does not define a job dependency between Jobs 43 and 45. Consequently, the job scheduler (Slurm) data contains no dependency information for these two jobs and no solid arrow is drawn in the visualization. Yet, even in the absence of Slurm dependency information our approach exposes job dependencies. Based on I/O activity recording [34], we track data dependencies and provide additional provenance data. In this example, the data dependency between Jobs 43 and 45 enforces a sequential execution of both jobs, resulting in inefficient resource utilization. While Jobs 43 and 44 run concurrently, Job 45 represents a load imbalance in the upper execution path of Figure 9.

Finally, after the completion of Jobs 44 and 45, Job 46 ends the workflow. Job 46 is a potential candidate for performance analysis, as this job exhibits the longest runtime of all jobs. In Job 46, Job Step 2 dominates the runtime. Any optimizations that reduce the runtime of this job will directly result in reduced runtime for the overall workflow.

*b) GATK/Cromwell:* To enable users to adopt our work in practice, options for a simple integration of the presented instrumentation system into existing workflow management systems are essential. This case study demonstrates such an integration using the workflow management system Cromwell [35] as example. Cromwell supports a Slurm backend transparently. Additionally, many implementations of realworld workflows are available for Cromwell. These workflows use the Genome Analysis Toolkit (GATK) [35] Java application.

We realize the integration into Cromwell by adding a parameterized extra wrapper layer to Cromwell's default Slurm back-end provider. This allows us to wrap each job submission (sbatch call) and makes our approach independent of a specific workflow example. The wrapper script creates a custom environment that controls the Score-P instrumentation [36] of each job and invokes OTF2-Profile to process any generated job trace. We also add an automatic epilogue step to all Slurm jobs that invokes JobLog to collect actual wall time and other accounting information of the job. Finally, we add two inputs to the workflow itself:

- The location of the Score-P wrapper script. Not all instrumentation configurations are appropriate for all
![](_page_7_Figure_0.png)

Fig. 11: Timeline view visualization of the Joint Calling Genotypes workflow from GATK.

workflows, so this is treated as a workflow level input.

- The Java executable to use. Score-P's runtime bytecode instrumentation relies on a Java wrapper, scorep-bc-java, in place of the Java executable. This cannot simply be part of the Score-P wrapper script, as not all workflows in Cromwell are Java-based.
We chose the Joint Calling Genotypes (JCG) workflow from GATK as our test case for Cromwell-based workflows. We applied user-level Java instrumentation to record the performance behavior of the (JCG) workflow. Figure 11 shows the results of our measurements. The JCG workflow consists of two phases.

In the first phase, JCG starts with a scatter/gather operation. This initial phase consists of a configurable number of parallel jobs. As Figure 11 shows, our example starts with three jobs (11643156 − 11643158). All three jobs have wellbalanced individual durations, indicating an adequate load balancing. However, not all jobs are scheduled concurrently. This suggests optimization potential for either end-to-end time or resource usage efficiency.

In the second phase, JCG performs a two-step serial analysis of results from previous jobs. Jobs 11643160 and 11643161 represent this subsequent post-processing in Figure 11. Jobs of the second phase depend on the jobs of the first phase, as they generate the input data for the post-processing step.

Cromwell manages workflow dependencies by its own internal polling mechanism. Hence, dependencies are not controlled via Slurm, and thus, are not included in available Slurm information. Nevertheless, our approach reveals these dependencies based on information obtained from I/O recording. Figure 11 illustrates these dependencies as dotted arrows between individual jobs. This allows our tool to visualize the internal workflow structure for the users.

*c) GROMACS:* The software suite GROMACS (Groningen MAchine for Chemical Simulation) [37] is an open-source package for molecular dynamics. Its main purpose is the simulation of biochemical molecules like proteins, lipids, and nucleic acids. This case study examines the "Lysozyme in Water" example [38].

The observed workflow consists of six jobs in one pipeline. Figure 12 gives an overview of the workflow topology. Figure 12a illustrates the topology in the dependency graph mode. The first three jobs prepare the simulation system. These jobs perform their work in a completely serial fashion. The last three jobs are parallelized and perform most of the simulation work. Figure 12a shows that the job steps of Jobs 12154375 to 12154377 spend a considerable amount of their time in I/O (yellow color) and MPI (red color) routines, suggesting these jobs as good candidates for optimization. However, Figure 12b provides additional insight by scaling the Job Boxes according to their actual runtime. This visualization indicates that the runtime share of Jobs 12154375 to 12154377 and also Job 12154378 is negligible. Instead, Jobs 12154379 and 12154380 appear to be promising candidates for further performance analysis. Especially Job Steps 2 and 5 of Job 12154379 and Job Step 2 of Job 12154380 dominate the overall runtime. All mentioned job steps are compute intensive (green color). Further analysis of Job Step 2 of Job 12154380 reveals an MPI runtime share of about 10 %. To identify the reason of this performance issue we inspect the recorded event logs.

The upper graph of Figure 13 shows the Vampir visualization of the corresponding event logs. The analysis exposes a load imbalance in function *fft5d execute*. Work is not evenly distributed across all processes. On some processes (e.g., *Master thread:11*) the execution of *fft5d execute* takes significantly longer than on other processes. As a result, processes with less workload start their MPI communication early but have to wait for processes with longer running *fft5d execute* instances. This increases the overall time spent in MPI for the Job 12154380.

We repeated this measurement with an improved load balancing setup. The lower graph of Figure 13 illustrates that this setup distributes workload evenly across all processes. This reduces the MPI time share of the job from 10 % to 6 %.

#### *A. Overhead*

In this section we discuss the overhead of our measurement infrastructure. We distinguish three potential sources of overhead: application instrumentation with Score-P, recording of job scheduling information with JobLog, and data postprocessing with OTF2-Profile.

Instrumentation is a critical aspect with respect to overhead as it might prolong the runtime of observed applications and generate large amounts of event log data. Overhead induced by instrumentation highly depends on the kind of instrumented events and their frequency of occurrence. As already mentioned, users can select categories of recorded events by adjusting the measurement process. In addition, Score-P supports filtering options to further refine the set of recorded events. In experiments conducted by Knupfer et ¨ al. [24] the runtime overhead stayed below 4%. We recommend measurement setups with at most 10% runtime overhead

![](_page_8_Figure_0.png)

(b) Timeline mode

Fig. 12: Topology of the GROMACS "Lysozyme in Water" workflow.

![](_page_8_Figure_3.png)

Fig. 13: Event log visualization of GROMACS Job 12154380, Job Step 2. The upper graph (blue background) shows an event sequence of the GROMACS run with disabled load balancing. The lower graph (white background) illustrates the corresponding event sequence of a run with enabled load balancing. The event sequences depict GROMACS functions (green) and MPI communication (red). Invocations of the function *fft5d execute* are highlighted in yellow.

in order to obtain results reasonable for performance analysis. In our experiments the GROMACS overhead was below 10%, whereas the GATK overhead was still quite significant (approximately 3× runtime) even with filtering. However, Java bytecode instrumentation has much higher overhead than compile-time or library-wrapping based instrumentation. The memory requirement to store event logs also correlates with the number of recorded events. Therefore, users can apply selective instrumentation and filtering to control memory consumption. The event logs of our use cases demanded at most 10GiB for the entire GATK workflow.

Recording of job scheduling information with JobLog is less critical. It records statistics in the range of 1 − 10kiB. Furthermore, our approach queries scheduling information after the application has finished and thereby does not affect the application execution.

Data post-processing with OTF2-Profile is also noncritical as it is run as a post-mortem task and can be executed on a local machine. Aside from a fixed setup time of 5−15 seconds, in our analyses the post-processing step ran for at most 10% of the original application runtime.

#### VI. CONCLUSION AND FUTURE WORK

The introduced top-down approach enables a comprehensive overview of a workflow's performance characteristics. It combines profile reports with detailed event trace analysis to guide users through the analysis of complex workflows.

Providing only one level of detail would be insufficient for workflow performance analysis. Separating the workflow analysis into multiple levels with different scopes is necessary to avoid overwhelming of users with performance details at initial stages. To provide guidance to performance issues we connect overview data with detailed recordings containing root causes of problems.

The capturing and analysis of I/O dependencies allows to detect unused parallelization potential in the workflow structure. Furthermore, it enables support for workflows that do not explicitly define their dependencies.

While implementing our approach, we developed and enhanced several tools to adequately cover the multiple analysis levels of workflows. Score-P records tracing data, OTF2- Profile creates summaries, JobLog captures scheduling information, and Workflow Visualizer processes the performance data to provide a graphical analysis of the recorded workflow.

We proved the applicability of our approach with three workflow analysis cases covering different analysis scenarios.

Our future plans include to analyze how efficiently jobs utilize their allocated resources. This information will help users or scheduling systems to optimize their resource allocation decisions. Therefore, we will enhance functionalities of our approach to compare multiple runs on the same system as well as on varying resources.

# ACKNOWLEDGEMENTS

This work is funded by the European Union's Horizon 2020 Research and Innovation programme under Grant Agreement number 671951.

#### REFERENCES

- [1] California Institute of Technology. (2019) Laser Interferometer Gravitational-Wave Observatory (LIGO). [Online]. Available: https://www.ligo.caltech.edu/ [Accessed October 01, 2019]
- [2] European Organization for Nuclear Research (CERN). (2019) Large Hadron Collider (LHC). [Online]. Available: https://home.cern/science/accelerators/large-hadron-collider [Accessed October 01, 2019]
- [3] M. Atkinson, S. Gesing, J. Montagnat, and I. Taylor, "Scientific workflows: Past, present and future," *Future Generation Computer Systems*, vol. 75, pp. 216 – 227, 2017. [Online]. Available: http://www.sciencedirect.com/science/article/pii/S0167739X17311202
- [4] B. Shneiderman, "The Eyes Have It: A Task by Data Type Taxonomy for Information Visualizations," in *Proceedings 1996 IEEE Symposium on Visual Languages*, Sep. 1996, pp. 336–343.
- [5] A. Barker and J. van Hemert, "Scientific Workflow: A Survey and Research Directions," in *Parallel Processing and Applied Mathematics*, R. Wyrzykowski, J. Dongarra, K. Karczewski, and J. Wasniewski, Eds. Berlin, Heidelberg: Springer Berlin Heidelberg, 2008, pp. 746–753.
- [6] M. Pierce, S. Marru, L. Gunathilake, T. A. Kanewala, R. Singh, S. Wijeratne, C. Wimalasena, C. Herath, E. Chinthaka, C. Mattmann, A. Slominski, and P. Tangchaisin, "Apache airavata: Design and directions of a science gateway framework," in *2014 6th International Workshop on Science Gateways*, June 2014, pp. 48–54.
- [7] The Apache Software Foundation (ASF). (2019) Taverna Workflow System. [Online]. Available: https://taverna.incubator.apache.org/ [Accessed October 01, 2019]
- [8] B. Ludascher, I. Altintas, C. Berkley, D. Higgins, E. Jaeger, M. Jones, ¨ E. Lee, J. Tao, and Y. Zhao, "Scientific workflow management and the KEPLER system," *Concurrency and Computation: Practice and Experience*, vol. 18, pp. 1039–1065, 08 2006.
- [9] E. Deelman, K. Vahi, G. Juve, M. Rynge, S. Callaghan, P. J. Maechling, R. Mayani, W. Chen, R. F. da Silva, M. Livny, and K. Wenger, "Pegasus: a workflow management system for science automation," *Future Generation Computer Systems*, vol. 46, p. 17–35, 2015. [Online]. Available: http://pegasus.isi.edu/publications/2014/2014-fgcsdeelman.pdf
- [10] E. Deelman, K. Vahi, M. Rynge, G. Juve, R. Mayani, and R. F. da Silva, "Pegasus in the cloud: Science automation through workflow
- technologies," *IEEE Internet Comp.*, vol. 20, no. 1, pp. 70–76, Jan 2016. [11] M. Mattoso, K. Ocana, F. Horta, J. Dias, E. Ogasawara, V. Silva, ˜ D. de Oliveira, F. Costa, and I. Araujo, "User-Steering of HPC Work- ´ flows: State-of-the-art and Future Directions," in *Proceedings of the 2nd ACM SIGMOD Workshop on Scalable Workflow Execution Engines and Technologies*. ACM, 2013, p. 4.
- [12] F. Costa, V. Silva, D. De Oliveira, K. Ocana, E. Ogasawara, J. Dias, ˜ and M. Mattoso, "Capturing and Querying Workflow Runtime Provenance with PROV: a Practical Approach," in *Proceedings of the Joint EDBT/ICDT 2013 Workshops*. ACM, 2013, pp. 282–289.
- [13] W. Yoo, M. Koo, Y. Cao, A. Sim, P. Nugent, and K. Wu, "Performance Analysis Tool for HPC and Big Data Applications on Scientific Clusters," in *Conquering Big Data with High Performance Computing*. Springer, 2016, pp. 139–161.
- [14] D. Krol, R. F. da Silva, E. Deelman, and V. E. Lynch, "Workflow per- ´ formance profiles: development and analysis," in *European Conference on Parallel Processing*. Springer, 2016, pp. 108–120.
- [15] E. Deelman, T. Peterka, I. Altintas, C. D. Carothers, K. K. van Dam, K. Moreland, M. Parashar, L. Ramakrishnan, M. Taufer, and J. Vetter, "The future of scientific workflows," *The International Journal of High Performance Computing Applications*, vol. 32, no. 1, pp. 159–175, 2018.
- [16] R. F. da Silva, R. Filgueira, I. Pietri, M. Jiang, R. Sakellariou, and E. Deelman, "A Characterization of Workflow Management Systems for Extreme-Scale Applications," *Future Generation Computer Systems*, vol. 75, pp. 228–238, 2017.
- [17] H. Casanova, S. Pandey, J. Oeth, R. Tanaka, F. Suter, and R. F. da Silva, "WRENCH: A Framework for Simulating Workflow Management Systems," in *2018 IEEE/ACM Workflows in Support of Large-Scale Science (WORKS)*, ser. WORKS'18, Nov 2018, pp. 74–85.

- [18] A. Singh, A. Rao, S. Purawat, and I. Altintas, "A Machine Learning Approach for Modular Workflow Performance Prediction," in *Proceedings of the 12th Workshop on Workflows in Support of Large-Scale Science*, ser. WORKS '17. New York, NY, USA: ACM, 2017, pp. 7:1–7:11. [Online]. Available: http://doi.acm.org/10.1145/3150994.3150998
- [19] A. B. Yoo, M. A. Jette, and M. Grondona, "SLURM: Simple Linux Utility for Resource Management," in *Job Scheduling Strategies for Parallel Processing*. Springer Berlin Heidelberg, 2003, pp. 44–60.
- [20] Altair. (2019) PBS Professional. [Online]. Available: https://www.pbspro.org/ [Accessed October 01, 2019]
- [21] IBM. (2019) IBM Spectrum LSF Suites. [Online]. Available: https://www.ibm.com/us-en/marketplace/hpc-workloadmanagement [Accessed October 01, 2019]
- [22] S. S. Shende and A. D. Malony, "The Tau Parallel Performance System," *International Journal of High Performance Computing Applications*, vol. 20, no. 2, pp. 287–311, May 2006. [Online]. Available: http://dx.doi.org/10.1177/1094342006064482
- [23] L. Adhianto, S. Banerjee, M. W. Fagan, M. Krentel, G. Marin, J. M. Mellor-Crummey, and N. R. Tallent, "HPCTOOLKIT: Tools for performance analysis of optimized parallel programs," *Concurrency and Computation: Practice and Experience*, 2010.
- [24] Dieter An Mey et al., "Score-P: A Unified Performance Measurement System for Petascale Applications," in *Competence in High Performance Computing 2010*, C. Bischof, H.-G. Hegering, W. E. Nagel, and G. Wittum, Eds. Springer Berlin Heidelberg, 2012.
- [25] A. Knupfer et al., "The Vampir Performance Analysis Tool-Set," in ¨ *"Tools for High Performance Computing", Proceedings of the 2nd International Workshop on Parallel Tools for High Performance Computing*. Stuttgart, Germany: Springer-Verlag, 2008.
- [26] M. O. McCracken, N. Wolter, and A. Snavely, "Beyond Performance Tools: Measuring and Modeling Productivity in HPC," in *Proc. of the 3rd International Workshop on Software Engineering for High Performance Computing Applications*. IEEE Computer Society, 2007, p. 4.
- [27] D. Eschweiler *et al.*, "Open Trace Format 2 The Next Generation of Scalable Trace Formats and Support Libraries," in *Applications, Tools and Techniques on the Road to Exascale Computing : Proc. of the 14th biennial ParCo conference*, ser. Advances in Parallel Computing, vol. 22, 2012, pp. 481–490.
- [28] H. Brunst and M. Weber, "Custom Hot Spot Analysis of HPC Software with the Vampir Performance Tool Suite," in *Proc. of the 6th International Parallel Tools Workshop*. Springer, Sept 2012, pp. 95–114.
- [29] M. Geimer, F. Wolf, B. J. N. Wylie, E. Abraham, D. Becker, and B. Mohr, "The Scalasca Performance Toolset Architecture," *Concurrency and Computation: Practice and Experience*, vol. 22, no. 6, pp. 702–719, 2010.
- [30] (2019) OTF/OTF2 Profile. [Online]. Available: https://github.com/scorep/otf2 cli profile [Accessed October 01, 2019]
- [31] MPI Forum. (2019) MPI: A Message-Passing Interface Standard. Version 3.1. [Online]. Available: http://www.mpi-forum.org/ [Accessed October 01, 2019]
- [32] OpenMP. (2019) The OpenMP API specification for parallel programming. [Online]. Available: http://openmp.org/ [Accessed October 01, 2019]
- [33] (2019) JobLog. [Online]. Available: https://github.com/harryherold/JobLog [Accessed Oct 01, 2019]
- [34] R. Tschuter, C. Herold, B. Wesarg, and M. Weber, "A Methodology ¨ for Performance Analysis of Applications Using Multi-layer I/O," in *Euro-Par 2018: Parallel Processing*, M. Aldinucci, L. Padovani, and M. Torquati, Eds. Springer International Publishing, 2018, pp. 16–30.
- [35] K. Voss, G. V. D. Auwera, and J. Gentry, "Full-stack genomics pipelining with GATK4 + WDL + Cromwell [version 1; not peer reviewed]," *ISCB Comm J*, vol. 6, no. 1381, 2017. [Online]. Available: https://f1000research.com/slides/6-1381
- [36] J. Frenzel, K. Feldhoff, R. Jaekel, and R. Mueller-Pfefferkorn, "Tracing of Multi-Threaded Java Applications in Score-P Using Bytecode Instrumentation," in *ARCS Workshop 2018; 31th International Conference on Architecture of Computing Systems*, April 2018, pp. 1–8.
- [37] D. Van Der Spoel, E. Lindahl, B. Hess, G. Groenhof, A. E. Mark, and H. J. C. Berendsen, "GROMACS: fast, flexible, and free," *Journal of computational chemistry*, vol. 26, no. 16, pp. 1701–1718, 2005.
- [38] J. Lemkul. (2019) GROMACS Tutorial "Lysozyme In Water". [Online]. Available: http://www.mdtutorials.com/gmx/complex/01 pdb2gmx.html [Accessed October 01, 2019]

