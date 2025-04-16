# **SPOTlight On Testing: Stability, Performance and Operational Testing of LANL HPC Clusters**

Georgia Pedicini High Performance Computer Systems Los Alamos National Laboratory P.O. Box 1663 MS-T080 Los Alamos, NM 87545 +1 505 667-8117 gap@lanl.gov

Jennifer Green High Performance Computer Systems Los Alamos National Laboratory P.O. Box 1663 MS-T080 Los Alamos, NM 87545 +1 505 665-8421 jgreen@lanl.gov

## **ABSTRACT**

Testing is sometimes a forgotten component of system management, but it becomes very important in the realm of High Performance Computing (HPC) clusters. Many large-scale HPC cluster installations are one of a kind, with unknown issues and unexpected behaviors. First, the initial installation may uncover complex configuration interactions that are only apparent at scale; Stability becomes a critical feature of early system testing. Second, Performance may be significantly impacted by small changes to the system. Third, after initial shakeout, users expect a system that is reliable on their terms; ongoing Operational tests verify reliability, and provide early warning of developing problems. A robust test suite should address all of these test categories, and present both tests and results in a manner that meets usability requirements. We will describe Los Alamos National Laboratory's current test suite, and the development project to expand the suite to cover these areas and provide better tools for analysis and reporting.

## **Categories and Subject Descriptors**

C.4 [PERFORMANCE OF SYSTEMS]: Reliability, Accessibility, and Serviceability; Stability, Performance, and Operational Testing; High Performance Computing;

## **General Terms**

Measurement, Reliability, Verification.

## **Keywords**

Reliability, Accessibility, Serviceability; RAS; Performance testing; Stability Testing; Operational Testing; Test framework; High Performance Computing; Test Driven Development; SPOT;

## 1. **INTRODUCTION**

Large HPC centers face special challenges when standing up a new cluster. Many large-scale clusters are unique with complex interdependencies. With exascale computing on the horizon, new challenges will be presented to high performance computing

Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and/or a fee. Copyright is held by the author/owner(s) *SC'11 International Conference for High Performance Computing,* 

*Networking, Storage and Analysis – Seattle,* WA USA Copyright 2010 ACM 978-1-4503-0771-0/11/11…$10.00. centers in system standup, integration, and operations. The computing environment will be exponentially more complex than the systems already in place, limiting (or, in some cases, prohibiting) manual testing and troubleshooting procedures, and will require a robust and dynamic testing system that scales well, is highly configurable and provides built-in and extensible results analyses interfaces.

## 1.1 **History of HPC at LANL**

Best practices in HPC at Los Alamos National Laboratory (LANL) developed from a long history of one-of-a-kind supercomputer installations. The unique environment and challenges require tailor made tests to perform verification of changes to system hardware, software and the users' environment. The development of a framework with which to conduct tests has been an on-going project since LANL's first cluster installation, Bluemountain, and has been developed over the years to accommodate dynamic HPC requirements.

## 1.2 **Problem Statement**

As pointed out in [7], supercomputers are "notoriously unreliable" due to frequency of failures caused by "the law of averages." The more components a system contains, the higher the probability is that a component will fail. Large HPC clusters are often built with new technologies, adding complexity to cluster maintenance. Since supercomputers aim at high utilization, the systems run under constant heavy workloads with very little downtime. These computers support mission critical applications and are scarce resources. This is why *Reliability, Accessibility and Serviceability* are such important qualities to uphold.

It is infeasible to develop a framework and test suite built around a static set of requirements, as the needs of the support team and the systems are constantly evolving based on current technology and user demands. Despite constant changes, the motivation for this project of ensuring the best possible levels of Reliability, Accessibility, and Serviceability has and will remain consistent.

## 1.3 **Testing philosophy**

The test suite and its framework comprise a project that requires a more flexible development model. In the past, the test suite was built in an ad hoc fashion to handle these changes, glued together using scripting languages and system tools. Our current project is to revamp the test suite to account for a broader user base, and to provide a flexible tool using a methodology that accepts a constantly changing set of requirements and priorities. We are working towards formalizing a test development process that embraces the evolutionary nature of clusters and environments and is engineered to gracefully accept and adapt to these changes.

# 2. **RESEARCH ON SOFTWARE TESTING**

The importance of testing a high-performance computer is indisputable. Users have high standards for performance and reliability; working towards delivering these standards contributes to the success of the installation of major systems. Unscheduled downtime of a production environment is very unfavorable; HPC centers should aim to minimize these interrupts by thorough, goaloriented testing efforts.

# 2.1 **Definitions**

For clarification of terms used in the context of this project, the next section defines terms whose definitions may be ambiguous.

#### *2.1.1 System Definitions*

A system is an entity that interacts with other entities, including hardware, software, humans, and the physical world with its natural phenomena. Systems are composed of components, each of which is another system, until the breakdown of system components result into those that are atomic. Systems provide services, which the users (also systems) use. For clarity, and due to the current state of high performance computing, we will use "cluster" to refer to the hardware installation and "system" for other components under discussion.

The boundary where the service delivery occurs is the service interface. From a user's perspective, the state that is perceivable at the service interface is its external state; all else is the system's internal state. The services provided by the system to the users are a sequence of the system's external states.

A service failure is defined as an event that occurs as a result of deviation (error) from correct service. Service outage is a period of delivery of incorrect service, while a service restoration is the transition from incorrect service to correct service. The cause of the error is called a fault, which can be internal or external to the system. Not all faults affect the external state of the system to cause a failure (active); dormant errors exist, as well [2].

# *2.1.2 Reliability, Availability and Serviceability*

Reliability is the probability that an item will function without failure under stated conditions for a specified amount of time [12]. "Stated conditions," indicates prerequisite conditions external to the item being considered. For example, a stated condition for a supercomputer might be that power and cooling must be available - thus a failure of the power or cooling systems would not be considered a failure of the supercomputer itself.

Availability is the fraction of a time period that an item is in a condition to perform its intended function upon demand ("available" indicates that an item is in this condition) [12].

Serviceability is the probability that an item will be retained in, or restored to, a condition to perform its intended function within a specified period of time [12].

Jon Stearley, of Sandia National Laboratory, in [12], aims at solidifying a definition set and metrics describing RAS, which is an important foundation from which to build consistency in performance measurements among multiple supercomputers and among various laboratories. While the number of components that make up large scale clusters increase, the potential for failure escalates according to growth. "The absence of agreed definitions and metrics for supercomputer RAS obscures meaningful discussion of the issues involved, hinders their solution, and increases total system cost." [12]

Having a solid means of extracting meaningful information from tests, we can gather information that is vital to many areas of cluster computing, including optimizing check-pointing in user codes. More relevant to our testing efforts, however, is that having solid measurements extracted from performance testing allows us to approach system maintenance with a more informed approach.

#### *2.1.3 Capability and Capacity Computing*

Capability computing is typically thought of as using the maximum computing power to solve a large problem in the shortest amount of time. Often a capability system is able to solve a problem of a size or complexity that no other computer can.

Capacity computing, in contrast, may be defined as using efficient cost-effective computing power to solve somewhat large problems or many small problems or to prepare for a run on a capability system [5].

# 3. **TESTING CATEGORIES**

Our testing is targeted to three categories of tests: Stability, Performance, and Operational Testing (SPOT). The following sub-sections describe what we mean by these terms.

# 3.1 **Stability Tests**

Large HPC centers face special challenges when standing up a new cluster. Many large-scale clusters are unique, whether a significant scale-up of existing technologies, or entirely new technologies. Each approach comes with inherent stability risks.

Clusters composed of existing technologies come with the vendor's recommended configuration details, and a collection of tools for system administration. Physical specifications include rack and unit placement, wiring diagrams, cooling requirements, etc. The first challenge is to make sure these physical requirements can scale properly, and conform to the local site. Changes to any part of this configuration can impact other aspects of the cluster. Another challenge includes the scaling of system administration tools and their ability to scale to large clusters. They are developed in the context of "reasonable-sized" clusters, and operate under a serial model. Many tools require parallel wrappers with error checking in order to scale to our clusters. Finally, the operating system makes assumptions about reasonableness. Each node logs "interesting" events, which has potential to overwhelm the system logs, as well as the network that these event messages travel over, with heartbeats and other messages related to nodes' states.

New technology has all of the same scale-up issues, along with the added risk of dealing with untested configurations. Again, the vendor provides recommendations and system tools, but when standing up a one-of-a-kind system, none of the details can be fully validated until it is on-site. No matter how much testing the vendor has done, their site is, by definition, an artificial environment compared to the HPC center in which it will be placed into production. For instance, local interconnect and authentication requirements may be highly customized.

As another example, file and storage systems are core subsystems at the heart of a HPC center. The path from the user's I/O call to the final file close is long and complex, involving the operating system, memory, interconnect, network switches, miles of cable, and finally the disk sub-systems, themselves. Users are understandably concerned about the file-systems; their calculations and simulations are useless if the results cannot be reliably stored. Thus, it is extremely important that the file and storage systems be validated early in the life cycle of the new machine.

#### *3.1.1 Acceptance Testing*

Acceptance testing is an integral part of the stand-up for LANL HPC clusters. The tests used in procurements often consist of micro-benchmarks, standard HPC benchmarks, and applications from the intended users of the cluster [8]. Acceptance is performed before and after shipment from the vendor and includes operational, performance, and stability testing. This last phase consists of system level tests and real application codes, run 24x7, measuring both the stability of the hardware and consistency of performance. We also calculate metrics such as Mean Time to Failure, for the system and the codes. Only when the desired level of performance is reached can the cluster move on to the final phases of system integration and ultimately, production.

#### *3.1.2 Integration Testing*

The integration phase typically overlaps acceptance testing, and is used to discover and investigate assumptions about the cluster and how it performs within a specific site. It is not unusual for configuration details to be modified during this phase. Integration tests have to adapt to these changes, to make sure the right thing is being tested. For example, the test suite might verify a standard system daemon whose function is considered critical. If local considerations require that the daemon be reconfigured to run on only a small subset of nodes, the test has to be modified. Other integration tests aim to characterize "normal" behavior for a new cluster. This may be simple updates to test threshold values, or may require completely new tests.

## *3.1.3 Summary*

LANL's experience with HPC clusters is often groundbreaking, as the architectures and environments that are supported are one-offs utilizing cutting edge technologies. This poses unique challenges regarding stability, for which LANL's HPC support team has developed a series of informal test suites. Our approach to stability testing begins even before a new system is onsite, by using test-bed environments to evaluate proposed products and components at small scale. The acceptance test suite carries this evaluation forward to the integration phase. When it's practical, we continue to use these test-beds to test upgrades, patches, or other "routine" maintenance before deploying on the production cluster(s). One goal of the SPOT project is to formalize these *Stability* tests and carry them forward into performance and operational testing.

## 3.2 **Performance Tests**

Once a new cluster is stabilized, performance testing should be designed to ensure that the production system is running at optimal performance. This begins with verification that it meets the contracted performance metrics. HPC clusters are rated according to industry accepted performance standards. Examples of these metrics include raw input/output (I/O) transfer rates, message passing rates, throughput, bandwidth, etc.

With this baseline established, we can measure how changes to the system (e.g., patches and reconfigurations) impact performance. Trend data representative of certain performance metrics allows us to track performance over the life of the cluster. The same acceptance tests can also be used for long-term trend analysis, but may not be the optimal set of performance tests for this purpose.

## *3.2.1 Baseline*

A baseline, in the context of cluster testing, is a measurement of system performance that is extracted from running the cluster under controlled conditions. On a new cluster, a portion of the acceptance suite may be used as a baseline reference point to compare results going forward. A production cluster's performance may deviate from the original performance requirements and specifications after stand-up. In order to establish a baseline on a production cluster, a representative sample of results should be extracted from many test iterations under similar operating conditions. This can be used as a comparison with acceptance criteria and acceptance test metrics to determine optimization or degradation of system performance since stand-up.

#### *3.2.2 Trend Discovery and Analysis*

Trend analysis is a means of identifying and extrapolating trends that exist within a dataset that are usually not apparent from visual inspection of the data. Analysis of data can be accomplished through graphing if the data size is appropriate for this type of analysis. Extremely large data, however, may require more sophisticated analysis, such as the use of mining algorithms (Kmeans, A priori, among others). Trend analysis is an important aspect of performance testing, as it may uncover otherwise unsuspected information about a cluster's performance. Comparison with established baseline performance standards and historical data collected from previous tests can help identify degraded performance leading up to a component failure.

Acceptance tests record performance under ideal conditions. A good starting point for a general performance test suite is to reserve time to re-run these acceptance tests, under the same conditions, whenever changes have been made. At a minimum, these runs establish a trendline for the base performance of the cluster.

The test suite design should consider that performance measurements depend on many variables, such as user load and environment settings. As the performance can substantially fluctuate depending on the context in which a test runs, a goal of performance test result interpretation is to account for every variable that affects performance, or else the results will be unreliable or misleading. Accurate trend analysis, therefore, must be careful to compare test information gathered from identical contexts (i.e., user load, allocation size and location, environment settings) when trying to identify changes in a system's performance. By having accurate representative performance metrics, the data can be used to compare system performance before and after changes.

#### *3.2.3 Load Testing*

Load testing is often confused with stress testing. The purpose of load testing is to uncover problems that occur at peak load. One method uses a series of very large jobs that the cluster should be able to handle. This is done to test the ability of an HPC cluster to handle a load that demand more resources than simple tests would. Another form of a load test is to run a mixture of job sizes up to the capacity of the cluster, testing its ability to handle and complex load. The purpose of load testing is to uncover problems that occur at peak load. Stress testing, on the other hand, serves the purpose of pushing the limits of the cluster to a point of failure in order to determine its limits, and is out of scope of this testing project.

# *3.2.4 Performance Metrics*

When considering HPC performance, it is important to identify what to measure, how to measure it, and what to compare it to in order to understand the measurement. These measurements provide a rich dataset representative of performance over time. This can be used to troubleshoot and identify problems before they cause failure, or to assist developers with determining application efficiency and optimization. Performance can also be correlated with system logging to identify areas needing improvement.

#### *3.2.4.1 Hardware Metrics*

A basic measure of computer performance is peak performance, the maximum performance rate possible for a given operation, measured in instructions per second, operations per second, and floating point operations per second [6]. Operations per second are based on the clock rate of the processors, and the number of operations per clock cycle. Processor speed is only one factor that impacts performance. Floating point operations per second historically have been the performance measure that held the most weight in acceptance criteria in procurement of supercomputers, however, at the chip level, communication speed plays and equally important role in determining performance. In addition, other hardware capabilities have huge impact on performance. These include speed between local memory and the chip, and speed between nodes. Communication speed is based on two major measurements: bandwidth and latency. Bandwidth quantifies the rate of data transferred, and is measured in bytes per second. Latency is a measure of the time it takes to get the first bit of information to the processor, measured in time units or clock periods. Communication speed impacts the useful performance of a parallel computer's hardware. Another measurement to consider in determining a parallel computer's performance is speedup. Speedup is the time improvement a given algorithm achieves when run on a parallel machine versus run on a single processor machine [6].

#### *3.2.4.2 Reliability Metrics*

Reliability metrics are important measurements in terms of cluster management. Stearley has contributed important work in quantifying reliability in HPC, proposing standardization of HPC measurements to improve tools and information sharing. The following represent measures of reliability:

- Mean Time and Node-hours Between System Failures
- Mean Time and Node-hours Between Node Failures
- Mean Time and Node-hours Between Job Interrupts
- Mean Time and Node-hours Between Service Interrupts

#### *3.2.4.3 Availability Metrics*

Following is a list of availability metrics used to quantify availability of HPC clusters:

- Total Availability
- Serviceability
- Mean Time to Boot System
- Mean Node-hours to Repair
- Total System Utilization
- Capability Usage Performance
- Scheduled System Availability

#### [11][12]

#### *3.2.5 Summary*

In practice, an HPC cluster may be primarily targeted to capability or capacity computing. However, a mixture of jobs provides the best overall data to perform trend analysis. Periodically running a capability level job, and collecting its performance data tracks long-term performance trends. Submitting a sample of small jobs in full system utilization verifies that the cluster is internally consistent, both for trend analysis and for operational testing.

An added benefit to including performance tests in a test suite is that each job can check a subset of the cluster. A spectrum of small jobs can effectively test the entire cluster by randomly sampling the cluster. In addition to tests that check other areas of user interest, such as access time and compile time, this provides a comprehensive test of the cluster's operation.

LANL's history of performance testing has generally focused on capability runs and specific features. I/O and network bandwidth are components that historically have been tested for performance, as they are especially prone to bottlenecks and contention. The SPOT project intends to broaden the range of *Performance* tests, and to improve analysis of data collected from them in order to provide a better characterization of the clusters' performance.

## 3.3 **Operational Tests**

Stability and performance testing naturally lead to operational testing. The general definition of operational testing is proactive testing to ensure that the cluster is functioning as expected. The two general cases are post-maintenance and ongoing background testing.

#### *3.3.1 Operational Testing Post-Dedicated Service Time (DST)*

Computers require regular maintenance. At LANL, monthly Dedicated System Time (DST) is set-aside on each cluster to perform maintenance, such as configuration changes, hardware replacements, firmware/software installation and upgrades for applications and operating systems. Testing is a fundamental part of any maintenance process and verifies that changes made to the system hardware and/or software didn't introduce unforeseen errors.

Operational testing builds from the previous base of stability and performance tests. Ideally, we verify that the cluster has returned to its 'normal' state of stability, with consistent or improved performance. In practice, these tests are best run in stages, stopping if a particular component fails a test so that the error can be resolved prior to continuing on with the rest of the suite. Exhaustive testing during this time is cost/time prohibitive, although testing should be adequate to identify problems.

#### *3.3.2 Background Testing*

A subset of operational tests can be run in the background to monitor real-time system health. Background tests should be tuned to have minimal impact on the overall system load. If possible, they should also run at non-peak times and in a preemptable mode.

It may be beneficial for the background suite to run a different set of tests than the standard operational suite. For example, postmortem analysis of system component failure may identify symptoms of a potential problem. New tests can then be added to check for those symptoms to better predict failure so that appropriate maintenance can be scheduled proactively.

#### *3.3.3 Summary*

While some operational tests are obvious, others will develop over time based on the experience with an installation. This category of testing will be dynamic over the life of the cluster, and requires updates to support new technologies. The SPOT project will build on the current suite of *Operational* tests in use at LANL.

## 4. **CURRENT TEST SUITE**

LANL's test suite is composed of about thirty-five tests that are used to perform verification on the clusters after DST and provide a nightly sanity check in the form of a cronjob. The test suite is loosely arranged around the commonly understood levels of unit,

integration, and system testing. Table 1 is a list of the test names and their primary function; additional aspects of the cluster are also verified as ancillary functions of the test.

## 4.1 **The Testing Framework**

The tests that perform health and software checks on LANL's HPC clusters work within a framework mainly written in Perl script. It calls specified tests and submits them to the scheduler. Each test saves output files to a temporary directory. After completion of the test suite, the framework gathers results from the individual tests and provides a pass/fail report that is viewable as standard output, or in the case of an automated test, is emailed to the test team. If failures occur, the output files for individual tests are saved and are easily inspected to determine the cause. Wrapper scripts orchestrate the setup and tear-down of individual tests.

# 4.2 **Specific Tests**

## *4.2.1 Node/Cluster Component Tests*

Cluster component testing verifies that the component meets requirements that were specified in its design, whether it operates as intended on the cluster to which it is installed, and that it continues to operate as expected in light of changes made to it and other components that it interfaces. Within this subset of tests, a selection of common commands are run, implementing a unit test concept of verifying that the cluster is minimally functional. We check for the synchronization of system time across a sample of nodes to ensure the Network Time Protocol Daemon (NTPD) is enabled and functioning as expected. File system connectivity and software version checks also exist in this category of tests.

#### *4.2.2 Node/Cluster Tools Tests*

This subset tests the batch system functionality on the clusters. The batch

system environment is a necessity and is present on all clusters at LANL. Tests include those that target the scheduler, the distributed resource manager, and test the function of specialty configurations, queuing, and submission parameters. This subset may be viewed as integration testing.

## *4.2.3 User Environment Tests*

User environment component tests ensure that the default user environment is functioning properly, including the module environment and several tools. Tests in this category load and test debuggers, versioning systems, scientific/math libraries, and run comprehensive checks on the module environment from the login nodes as well as on the compute nodes.

#### *4.2.4 Collection of Simple Serial Codes*

These tests consist of simple "hello world" codes in supported programming languages. The codes are compiled, linked, and executed on the front end and a compute node to verify that the

| Primary Test Elements |  | Secondary Test Elements |
| --- | --- | --- |
| Node/cluster Component Tests: |  |  |
| GENERIC INFO AND VERSIONS | Cluster environment test assortment |  |
| System clock skew within a given |  | Default C compiler, MPI library, ability |
| ntpd | allocation | to submit back-end job |
| Read/write functionality to Panasas |  |  |
| panasas read write test | scatch spaces | Performance statistics |
| Node/Cluster Tools Tests: |  |  |
| drmchk | Moab commands | Perl installation and library |
| Distributed Resource Manager |  |  |
| drm versions | (DRM) version number | DRM availability |
| Icstat | "Icstat" command |  |
| ljobs | "Ijobs" command |  |
| msubchk | Simple MOAB commands |  |
| MOAB's "msub" command and a |  |  |
| msub parameter tests | variety of "msub" parameters | "naccesspolicy" parameter |
| preempt | Scheduler preemption job Checks "-A standby" account existence in A MOAB "msub" | "mdiag -n" command |
| command. The account "standby" | takes on a low priority and preempt able configuration to allow low |  |
| priority jobs to run when resources |  |  |
| standby | become available. | Tests "msub" command |
| User Environment Component Tests: |  |  |
| modules test | Module environment | Moab job submission |
| Subset of module environment, |  | Limited testing of license server |
| compiler Mods | compiler functionality | connectivity. |
|  |  | Limited testing of license server |
| idl | IDL module files | connectivity |
|  |  | Limited testing of license server |
| tvdefault | Totalview default module | connectivity |
| Subversion module file (or default |  |  |
| svn command) and its functionality |  |  |
| svn basic tests | on the front- and back-ends | "msub" command |
| Collection of Compile/Link/Run Tests of Simple Serial Codes: |  |  |
| Default C. C++, and Fortran |  |  |
| helloC; helloCC; helloF90; helloFC; | compilers; default PGI version; | Limited test of license server |
| hello gcj java; hello sunjava 156 | GCC Java; Sun Java | connectivity and "msub" command |
| Collection of Compile/Link/Run Tests of Simple MPI Codes: |  |  |
| mpi gcc default; | Default compilers with their |  |
| mpi intel default; | corresponding default OpenMPI |  |
| mpi pathscale default; | libraries. MPI functionality on |  |
| mpi pgi default; | different sized jobs (varies with | Licensing, msub command, dependent |
| mvapich11_gcc433 | cluster) | job, possibly special versions |
| AMD Core Math Library's |  |  |
| acml | functionality | Intel and PGI compilers |
| User Environment Functional/Performance Tests: |  |  |
| Performance test of cluster's ability |  |  |
| to execute Algebraic Multigrid |  | "msub" command, node interconnect |
| boomerAMG | algorithm | speed and performance. |
| Performance test of system |  | PGI compiler module availability and |
| hydro64 | running sample user code | OpenMPI library |
| Performance test of system |  | Default PGI compiler module |
| sweep3d32 | running sample user code | availability and OpenMPI library |

#### **Table 1. Summary of Tests**

compilers and libraries are uniformly available and that they function as expected.

#### *4.2.5 Collection of Simple Parallel Codes*

This subset of tests was developed from the MPI Testing Tool (MTT) repository available at Indiana University. LANL is primarily an OpenMPI site, but we do support mvapich2 on some clusters. The 36 tests in this subset verify MPI conformance across the default compilers and MPI libraries available on each cluster. The codes are compiled and linked on the front-end, and then submitted for execution to a multi-node allocation via the job scheduler. Again, the goal is to verify that all the necessary tools are uniformly available and functioning as expected. In addition, the earlier simple tests of batch system functionality are verified in the context of a realistic user load.

#### *4.2.6 User Environment Functional/Performance*

Once all of the other tests have passed, the last category of testing utilizes code provided from the user community to verify that the overall system is functioning as expected. Davis, et al, in [3], argues that the benchmarks most representative of workload are actual applications. At LANL, we utilize local applications as a check that performance is up to standards, by measuring a timeto-solution on several codes. Performance deviation from "golden" output files is considered failure, and is tuned to each cluster. Custom-built, local codes test inter-nodal communication speed, I/O bandwidth, and access speed to network attached storage systems.

## 4.3 **Benefits and Shortcomings**

By using a test suite to verify installation, configurations, hardware and software on the clusters at LANL, we have detected and remedied issues, ranging from simple oversights in installations/configurations, to major problems, such as switch failure and node death. This testing process has become accepted as a last step in maintenance on all production clusters at LANL, assuring that the clusters are returned to users in the expected operational state.since it assists the maintenance staff in verifying that the clusters are returned to their expected operational state after changes and provides a consistent means of checking.

Unfortunately, the current framework has a high overhead, in terms of both disk usage and in the learning curve required for maintenance and debugging failures. Porting the test suite framework to new clusters is tedious, and many new feature requests have been identified that would greatly enhance its effectiveness.

## 5. **NEW DEVELOPMENT PROJECT**

Although the current test suite's value is recognized by the HPC group, we realize that there are areas of testing that we are not accomplishing as we should, and the framework with which we test has limitations. Stability, Performance and Operational Testsuite (SPOT) is a framework that will replace the current framework.

## 5.1 **Project Goals**

Goals of the SPOT project are to implement the same functionality of the framework currently used to perform postDST and nightly testing, and to do it better. The first step for developing this software is to determine functionality requirements in collaboration with subject matter experts and the testing team. Initial deployment will target baseline requirements, while further development iterations will address other desirable features.

## 5.2 **Requirements**

Our initial requirement elicitations have resulted in a set of requirements that will frame the design through several iterations of development.

General requirements for the new testing software include:

- 1. Broad usability for test users and analyzers. Broad definition of "environment," extending beyond on-node
execution, to include networks, file-systems, storage, and extending beyond the boundaries of LANL.

- 2. Well-defined interfaces for test input and output; include ability to bi-directionally share information with other data gathering/analyzing systems.
- 3. Test repository for adding and running tests, broadly available, yet controlled and organized allowing for searching and rating of tests within categories. Support for automated and on-demand testing modes.
- 4. Data repository with simple interface to view and search results, ranging from simple reports to visualization of trends.
- 5. Analysis should be able to characterize failure modes by category. "Known" failures should be mapped to appropriate tests.

Core requirements are the key components that the testing framework should implement. They can be generally categorized into interfaces, processes, storage, data that is collected, and information extracted from that data. From analyzing the general and core requirements, it is apparent that multiple sub-projects could fall out of the SPOT project.

*Test Framework Repository* – the framework requires strict version control in order to provide a stable product. It is to be available for download and portable across multiple clusters, though highly configurable to account for variability among clusters.

*Test Repository* – individual tests also require strict version control, in a separate repository. If the tool is to be of benefit to specialty groups, it should be accessible to them and be simple to use. The user interface for this repository should encourage teams to contribute to the testing project through a use case definition interface, where they can develop and their own tests and the required associated metadata. This tool will allow test maintainers to update and version-control their tests. The tests will be categorized by type, filterable and graded based on quality. A feature that is desired for the test repository is a traceability matrix of known failures to appropriate tests.

*API* - one issue with the current test suite is the lack of documentation on how to write and add a test to the suite. An API for this framework, since its user base is going to be a variety of people from various backgrounds, must be as easy to use and as hassle free as possible.

*Results Database* – to be used for performance analysis and regression, and accessible to other analysis tools. Results also must be provided in a selectable and exportable report format to support data analysis extensions. Output files and interim results must be available after the tests run for debugging purposes, but need not be retained indefinitely.

*Interfaces* - Multiple interfaces have been identified that are required in order to successfully meet the general and specific requirement set. They include:

- oCommand line interface
- oCron interface
- oResults storage interface
- oWeb results display interface
- oDatabase backend administrative interface
- o Database frontend user interface (queries) against results sets

- oInput definition interface
- oUse case development interface

## 5.3 **Similar Projects**

The Inca Test Harness is a similar project that is used to perform verification of the quality of service agreements for virtual organizations that host resources on the TeraGrid project. One feature of this tool is the emphasis on running all tests from a standard user account, addressing the unintentional disparity that can occur between privileged and unprivileged accounts. Their framework satisfies a similar requirement set, however, the focus is as a collector of individual testing "clients" across multiple HPC systems [10].

TETWare is a framework for testing software development projects across multiple operating systems. The tool has also been applied to a variety of testing applications where automated, repetitive testing is required. The goal is to provide a common user interface for all tests, allowing developers to concentrate on the tests, themselves [13].

Other test frameworks that are used in large HPC centers are Gazebo and Cbench. Gazebo was developed at LANL and is used to execute the acceptance tests on new HPC clusters [Idler, et al]. Cbench was developed at Sandia National Laboratories (SNL) to automate the integration testing efforts for the clusters at SNL [9].

Each of these tools can be customized to different environments and, potentially, to different purposes than their original intent. As the SPOT project progresses, we will continue to assess tools such as these to determine if an existing framework or independent modules from one or more of these projects can be used or modified to meet our requirements.

# 5.4 **Agile Development Model**

In order to conform to the constraints posed in a constantly evolving requirements set, we have adopted an Agile Development Model [1] that iterates over the development steps of gathering, defining and analyzing requirements, prioritizing them, and then implementing them in testable code. With each development cycle, the finished code is a usable and testable version or component of the software that is able to shift into production. Using this technique of coding in short bursts, we will be able to place the software into production in shorter time, and adjust the development project as we learn about how it will behave in a production environment and as its requirements change.

## 5.5 **Test Driven Development**

In addition to the adoption of the Agile System Development Lifecycle, a Test Driven Development (TDD) Methodology will be adopted. This will be of benefit to the end product since, by definition of TDD, with each finished product we will have a unit test suite that performs verification of the code. This will be valuable, as it will allow for regression testing of the framework ensuring stability of each release. This will create confidence in the test suite's ability to test the clusters. Having unit tests for the test suite will also be a useful tool to project teams that contribute to the test suite, increasing confidence that modules or extensions to the code-base do not inadvertently break the software they are extending.

## 5.6 **Development process considerations**

A test-driven development approach simply means that unit tests are written prior to actual source code development. By analyzing the test's failure modes first, we ensure a more complete understanding of the issue we are testing. Actual code development should then be much simpler as the programmer has already examined the problem from multiple angles. As with most quality assurance processes, it may seem like more work, and, initially, it will require more time to create source code. The benefits of programming in this way will be revealed as the project progresses. A well-implemented suite of unit tests provides quick verification and validation of each new release of the test suite. Finally, by developing good exception handling, we ensure that when implemented, each test will be more effective in reporting actual error conditions. Otherwise, critical system time can be wasted debugging the test software during production runs.

## 6. **SUMMARY**

Cluster testing efforts in production environments are sparse and are generally homegrown, informal tests. By adopting robust testing processes and developing software to support them, we can give the user community more confidence in the HPC resources they utilize, and provide detailed feedback about the machines that will enable them to make more informed choices in how they develop code on the systems. We can reduce unnecessary failures by better understanding faults and scheduling fixes before users' jobs are impacted. Already, supercomputers have grown to sizes unmanageable without the proper tools to support them; testing tools will become ever more important in this environment.

All too often, testing is an overlooked aspect of system design, installation, or maintenance. Approaches to cluster testing are under-developed in comparison with other types of computing. Los Alamos has a history of *Stability* and acceptance test suites, of ongoing *Performance* testing, and of *Operational* testing, on all of our high performance computers. The goal of the SPOT project is to carry these testing practices forward, improve the analysis and reporting mechanisms, and tie them all together as an integrated, robust test suite.

## 7. **ACKNOWLEDGMENTS**

The authors would like to thank the system administrators, integration teams, and other support personnel in the High Performance Computing Division at LANL for their input and insights to the SPOT project and to this paper.

Los Alamos National Laboratory, an affirmative action/equal opportunity employer, is operated by Los Alamos National Security, LLC, for the National Nuclear Security Administration of the U.S. Department of Energy, under contract DE-AC52- 06NA25396. LA-UR-11-1145, approved for public release, distribution is unlimited.

# 8. **REFERENCES**

- [1] *The Agile Manifesto*. http://agilemanifesto.org/ 2001.
- [2] Avizienis, Algirdas, Laprie, Jean-Claude, Randell, Brian and Landwehr, Carl. 2004. Basic concepts and taxonomy of dependable and secure computing. In *IEEE Transactions on Dependable and Secure Computing*, 1(1):11–33.
- [3] Davis, L.P., R.L. Campbell Jr., W.A. Ward Jr., and C.J. Henry. 2007. High-Performance Computing Acquisitions Based on the Factors that Matter. *Computing in Science and Engineering, vol. 9*, no. 6, pp. 35–44.
- [4] Ghemawat, S., Gobioff, H. and Leung, S.T. 2003. The Google file system. In *Proc. Of the 19th ACM Symposium on Operating Systems Principles (SOSP'03).*

- [5] Graham, S., Snir, M., and Patterson, C. Eds. 2005. *Getting up to Speed: The Future of Supercomputing*, National Academies Press. Washington, D.C.
- [6] Koniges A. E. Ed. 2000. *Industrial Strength Parallel Computing*, Morgan Kaufmann Publishers. San Francisco, CA.
- [7] Mitchell, B. IBM Blue Gene: the world's most advanced supercomputer from International Business Machines will tackle Grand Challenge problems. http://compnetworkingabout.com/library/weekly/aa051902a. htm. Accessed June, 2011.
- [8] Müller, M.S., Juckeland, G., Jurenz, M., and Kluge, M., 2007. Quality Assurance for Clusters: Acceptance-, Stress-, and Burn-In Tests for General Purpose Clusters. Springer-Verlag Berlin Heidelberg.
- [9] Ogden, J. Cbench: A Software Toolkit for Testing, Benchmarking, and Qualifying HPTC Linux Clusters.

Whitepaper. Sandia National Laboratory. http://sourceforge.net/projects/cbench-sf

- [10] Smallen, S., Olschanowsky, C., Ericson, K., Beckman, P., Schopf, J.M. The Inca Test Harness and Reporting Framework. 2004. In *Proceedings of SuperComputing '04*.
- [11] Stearley, J. 2005. Defining and measuring supercomputer Reliability, Availability, and Serviceability (RAS). *Proceedings of the Linux Clusters Institute Conference*, 2005.
- [12] Stearley, J. 2005. Towards a Specification for Measuring Red Storm Reliability, Availability, and Serviceability (RAS), *Cray Users Group Conference*.
- [13] *TETWare.* 2009. The Open Group. tetworks.opengroup.org.

