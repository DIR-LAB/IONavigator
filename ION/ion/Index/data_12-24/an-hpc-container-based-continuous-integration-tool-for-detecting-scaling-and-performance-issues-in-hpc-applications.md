# An HPC-Container Based Continuous Integration Tool for Detecting Scaling and Performance Issues in HPC Applications

Jake Tronge , Jieyang Chen , Patricia Grubel , Tim Randles , Rusty Davis , Quincy Wofford , Steven Anaya , and Qiang Guan

*Abstract***—Testing is one of the most important steps in software development–it ensures the quality of software. Continuous Integration (CI) is a widely used testing standard that can report software quality to the developer in a timely manner during development progress. Performance, especially scalability, is another key factor for High Performance Computing (HPC) applications. There are many existing profiling and performance tools for HPC applications, but none of these are integrated into CI tools. In this work, we propose BeeSwarm, an HPC container based parallel scaling performance system that can be easily applied to the current CI test environments. BeeSwarm is mainly designed for HPC application developers who need to monitor how their applications can scale on different compute resources. We demonstrate BeeSwarm using three different HPC applications: CoMD, LULESH and NWChem. We utilize GitHub Actions and provision resources from Google Compute Engine. Our results show that BeeSwarm can be used for scalability and performance testing of a variety of HPC applications, allowing developers to monitor application performance over time.**

*Index Terms***—Scalability test, continuous integration, high performance computing, cloud computing, container.**

# I. INTRODUCTION

S OFTWARE quality is extremely important in software development. Quality is complicated by the fact that many applications are growing in complexity day-by-day from the many contributions of developers on large teams around the

Manuscript received 9 March 2022; revised 20 November 2023; accepted 23 November 2023. Date of publication 29 November 2023; date of current version 6 February 2024. This work was supported in part by the National Science Foundation under Grants #2212465 and 2217104, in part by the U.S. Department of Energy through the Los Alamos National Laboratory under Grant LA-UR-21-28028, and in part by Los Alamos National Laboratory is operated by Triad National Security, LLC, for the National Nuclear Security Administration of U.S. Department of Energy under Grant 89233218CNA000001. Results presented in this paper were obtained using the Chameleon Cloudsponsored by the National Science Foundation. Recommended for acceptance by E. Damiani. *(Corresponding author: Qiang Guan.)*

Jake Tronge is with Kent State University, Kent, OH 44240 USA, and also with Los Alamos National Laboratory, Los Alamos, NM 87545 USA (e-mail: jtronge@kent.edu).

Jieyang Chen is with the University of Alabama at Birmingham, Birmingham, AL 35294 USA (e-mail: jchen3@uab.edu).

Patricia Grubel, Tim Randles, Rusty Davis, Quincy Wofford, and Steven Anaya are with Los Alamos National Laboratory, Los Alamos, NM 87545 USA (e-mail: pagrubel@lanl.gov; trandles@lanl.gov; rustyd@lanl.gov; qwofford@lanl.gov; sanaya@lanl.gov).

Qiang Guan is with Kent State University, Kent, OH 44240 USA (e-mail: qguan@kent.edu).

Digital Object Identifier 10.1109/TSC.2023.3337662

world. Continuous Integration (CI) [1] attempts to measure software quality in these complex settings and is widely adopted in many software development projects. A central CI server can be dedicated to testing.Whenever a developer makes a commit of her work to the central code repository, or upon certain triggers, such as the merging of a pull request, the server can automatically make a clone of the project and run a set of pre-designed test cases, and therefore constantly monitor software correctness and report potential problems in a timely fashion.

Existing CI typically focuses on software correctness, however, when it comes to HPC applications, *performance* and *parallel scaling* are just as important in measuring software quality since the applications are usually designed to deliver high performance and high throughput on large scale computing platforms. Parallel scaling of HPC applications is usually interpreted by how much speed up can be obtained if given more compute resources. Better scaling means that the HPC application can use the underlying computing resources more efficiently while constantly delivering good performance on a variety of computing resources. As an example, Fig. 1 shows how performance of the Legion system changes from commit to commit. Legion [2] is a parallel programming framework for distributed machines, designed to handle most data transfer and management tasks, using data properties, such as locality. Being able to see performance and scalability in real time like this can be extremely beneficial to the development process.

For HPC applications it can be difficult to know when certain commits could cause performance changes. Commits that may implement a bug fix could inadvertently introduce major performance problems. During an existing CI process the correctness tests would pass, but the performance issues may not reveal themselves until execution on a production system. In cases of critical applications these issues could cause major wastes of energy, time and money. Instead, we propose a solution to catch these issues early, before the applications ever leave a development stage.

There are existing solutions that can test performance with CI using plugins or special systems, but these are often not applicable to HPC because of the complexity of the applications, their requirements and portability issues. BlazeMeter [4], plugins for Jenkins[5], PerfCI [6] and others all offer existing CI performance solutions. However, these tools are not suitable for analyzing performance with HPC applications. Some systems,

1939-1374 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

![](_page_1_Figure_2.png)

Fig. 1. Example: the performance of Legion [2] changes as developers make progress. The performance is obtained by running a benchmark PENNANT [3] on the Legion system. The test suite sedovbig3x30 running on 10 processes (CPU cores) is used.

such as Jenkins, are very extensible and allow developers to implement their own CI system; this, however, can be extremely time consuming and difficult to do correctly. BlazeMeter, on the other hand, is not designed for testing HPC applications, but rather for testing web interfaces and application GUIs. PerfCI is designed for Python applications specifically, whereas HPC applications are written in Python as well as many other languages. The lack of a general performance analysis CI tool is a major issue for HPC developers, since being able to use CI-driven performance results can greatly improve software quality and development progress. It's also important to note that such a solution could be useful for more general scalability testing of other non-HPC applications, especially any that rely on a container and can utilize multiple nodes in the cloud.

This work presents new research on our CI performance and parallel scaling system for HPC applications that can be used with existing CI – BeeSwarm, based on a modified version of the Build and Execute Environment (BEE) [7]. This article is an extended version of a short paper that was previously published in 2021 [8]. The key contributions of this work are:

- The design and implementation of a general CI scalability testing tool with support for HPC-specific workflows.
- An analysis of different versions (commits) of an existing application to show how scalability testing can be useful for understanding performance changes over time.
- A demonstration of how cloud resources can be used for scalability testing, even with multiple nodes.

The rest of this article is organized as follows. In Section II, we give background that can help readers understand this work. We provide design details of BeeSwarm in Section III followed by evaluation and overhead in Section IV. In Section V we talk about future research directions and limitations. Section VI discusses related work. Finally, Section VII concludes our the article.

# II. BACKGROUND

HPC applications are almost always specially designed for performance and, because of this, often have complex configurations and dependencies. Some applications are even specially designed for certain clusters to achieve the greatest scalability. All these factors can make it extremely difficult to rerun HPC applications on other platforms, and also extremely difficult to run CI tests. To overcome these problems, we base BeeSwarm on BEE, which attempts to abstract application complexity and make applications easily portable across systems. BeeSwarm can then be used in a CI environment in order to configure and run scalability tests of an HPC application. Tests can be further configured and managed by CI environments, such as GitHub Actions[9], allowing developers to choose when they want to run particular scaling tests.

# *A. Build and Execution Environment (BEE)*

BEE [7], [10], [11] is a containerization environment and workflow orchestration system that enables HPC applications to run on both HPC and cloud computing platforms. Some of BEE's key features include: (i) *automation* of the deployment and execution environment; (ii) *portability* of scientific applications from HPC systems to the cloud and even to local machines; (iii) *flexibility* to choose from different environments and different compute backends all without dealing with underlying system complexities; (iv)*reproducibility* of scientific workflows allowing scientists to easily rerun experiments and get the same results; and finally (v) *provenance* to allow for documentation and archival of workflow metadata, the workflow graph and key run time statistics.

BEE is divided into several major components, including the Workflow Manager, the Task Manager, a Graph Database and the client. These components are shown in Fig. 2. The Workflow Manager, Task Manager and Scheduler all present well-defined REST interfaces for communication. Using a REST interface also makes it easy to run components on separate but connected systems. For example one might run a Task Manager component on a node in the cloud, while a user could run the Workflow Manager on their local machine. Some sort of connection, such as an SSH tunnel, can be used to connect the Workflow Manager and Task Manager and allow the REST API to be used again for communication.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:04:55 UTC from IEEE Xplore. Restrictions apply.

![](_page_2_Figure_1.png)

Fig. 2. Diagram of the main BEE components and communication methods.

The Workflow Manager acts as the central point of control. It parses workflows written in the Common Workflow Language (CWL) [12], and generates a Directed-Acyclic Graph (DAG) that is inserted into the Graph Database. When a workflow is executed, ready tasks are pulled from the generated DAG, and then sent to the TaskManager through its REST interface in order to be executed. Status updates, I/O metadata and other requirements are all managed by the Workflow Manager, ensuring that the workflow executes all tasks within a proper environment and configuration. The Task Manager is used to launch and monitor individual tasks on a system. When BEE is running on an HPC system, the Task Manager will typically communicate with an HPC resource manager such as Slurm [13] or IBM LSF [14]. When the Task Manager receives a task description from the Workflow Manager it will generate a batch script based on the task and send it to the resource manager to run when required resources are available. The Task Manager uses the resource manager's API to check the status of the task and will update the Workflow Manager when tasks change states. The BEE Client is an interactive client designed to easily allow users to package, submit and monitor their workflows.

A major initialization component of BEE is the Cloud Launcher script. The Cloud Launcher script is used for setting up cloud-based systems and clusters using a specified cloud configuration. The cloud configuration implemented in BEE is based on a cloud-specific template file and a YAML-formatted config. The template itself is implemented using Jinja2 templates[15], which allows for easy management of more complex cloud configurations. The YAML template file is loaded into the BEE Cloud Launcher and the parameters are used for generating the final cloud template that will be passed to the underlying cloud provider instance. This is similar to some of the cloud configuration tools used for some Google Compute Engine [16] instance set ups, but is BEE specific and also allows support for other cloud platforms based on OpenStack [17].

# *B. Scalability Testing*

Scalability testing attempts to measure how well an application is able to scale. This measure can be used on a range of test cases in order to make estimates about how an application will scale on a full-production system. These estimates can help developers determine whether or not their application is ready for a production run. In general there are two types of scaling tests, strong scaling and weak scaling [18]. Strong scaling tests typically use a fixed problem size and steadily increase the number of compute nodes or cores. Ideally, as the number of nodes used increase, the total execution time should decrease proportionally. For weak scaling both the problem size and the number of nodes or cores are increased proportionally. In this case, the goal is that the time remains the same as the problem size and resource count increase. For our tests we focus on doing strong scaling, but weak scaling could also easily be configured with BeeSwarm. It's important to realize, however, that each application is different and may require a specialized scaling configuration depending on the problem being solved and the limits of the application itself.

# *C. Continuous Integration (CI)*

CI was first named and proposed by Grady Booch in 1991. Originally, testing was done in local development environments, but as applications and the number of developers grew, centralized build servers became necessary. Today, many developers, including HPC developers are now using CI. For example, almost all projects in Next-Generation Code Project in Los Alamos National Laboratory are using CI [19].

Currently, there are many CI tools available to developers such as Travis CI, GitLab CI, Circle CI, Codeship, GitHub Actions, etc. However, the current design of CI services only focus on detecting software bugs in HPC applications. There are few CI tools which support parallel scaling and performance testing. BlazeMeter [4], PerfCI [6] and others offer performance testing frameworks, but are limited to specific domains. PerfCI is designed specifically for Python projects, and is thus not applicable to HPC applications which can be written in many different languages. BlazeMeter is built for testing systems, services, and frameworks, especially for web applications. They offer testing on mobile devices for applications, as well as the ability to do stress testing of web APIs and frameworks, such as by increasing the number of simulated users. HPC applications require much lower-level access to nodes and hardware in order to do testing, which is not provided by any of these frameworks. Therefore to the best of our knowledge, BeeSwarm is the first to provide parallel scaling CI for HPC applications.

# III. DESIGN

We develop BeeSwarm as a general solution that can be deployed with any CI service and any BEE-supported computing platform. We demonstrate BeeSwarm with a number of different node configuration using GitHub Actions [9] and Google Compute Engine [16]. The architecture of BeeSwarm is based on the BEE workflow orchestration tool. During the CI process, BEE is deployed in the test environment and it is then responsible for allocating resources and running the applications. Fig. 3 shows the CI pipeline we use with BeeSwarm. Once commits are made to the central repository, a script will install and launch BEE on the CI server which then reserves compute resources

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 20:04:55 UTC from IEEE Xplore. Restrictions apply.

![](_page_3_Figure_2.png)

Fig. 3. Overall CI pipeline for running scaling tests with BeeSwarm.

in the cloud, runs the tests with BEE and saves the results for later analysis. Since BeeSwarm is triggered by the particular CI tool, it can be configured to run exactly when the developer wants scalability tests to be run. For instance, an application could have the scalability test only performed on merge into a main branch of a repository, or upon opening a Pull Request. Software projects with long commit histories can easily run tests on multiple versions of the code, including the latest versions, in order to gather a sense of how new commits will affect the performance of the system.

# *A. BeeSwarm CI Client*

BeeSwarm adds a new CI-based client on top of BEE for managing BEE and multiple performance testing workflows in a CI environment. BEE was designed to make running portable workflows easy to run on HPC systems, cloud systems and within general development environments. The existing design of BEE includes an interactive client that gives the user the choice to submit, launch, package, archive, and rerun existing workflows. With BeeSwarm, we needed a different type of client component that could be used for multiple-workflow orchestration in a headless-CI environment. This tool acts as a drop-in replacement for the BEE interactive client, communicating with the existing endpoints in the other BEE components. The tool doesn't require any major changes to the other BEE components but simply changes the front-end that is used within the CI environment. The API configuration is relatively simple to do since the other components all communicate using REST APIs. Workflows launched and tested using BeeSwarm should be able to run with BEE in the normal HPC environment with no other modifications required.

The BeeSwarm CI Client itself is organized as a set of scripts that can be added to an existing repository. These include a set of wrapping shell scripts and environment set up scripts that install and create the base configuration for BEE. The main code for the run time execution within the CI environment is stored in a python script that launches, manages and connects to all of the BEE components. This script is also designed with a number of sub options that are used for configuration, management and debugging of CI scaling workflows. Configuration is specified through a YAML file and environment variables passed in by the CI system.

# *B. Workflow and Scalability Test Configuration*

The BeeSwarm CI-client pulls in scalability test configurations from a YAML-formatted file. This includes a number of BEE configuration options, such as the ports used for the REST APIs and also general information about the repository and the owner. The most important parameter of the configuration, however, is the *scale_tests* option which contains a list of scalability tests to run, corresponding workflow files and container configuration options. Upon launch in the CI environment, the scaling tests are run one-by-one and a profiling file is output by BEE's workflow manager in a JSON-format. Upon test completion, git is used to commit these profiles and other text files that have been produced by the scaling tests for usage by analysis tools.

Running scalability tests often requires changing many configuration options, such as for the container build or compilation process, the command-line flags passed to the binary, or the environment configuration. BEE is designed to run workflows written in the Common Workflow Language (CWL)[12]format. While CWL allows for a variety of options that can change how programs are executed during runtime, it is often not easy to work with when writing multiple similar, yet slightly different workflows. For example, to run a strong scaling test for a particular application, one may need to change the number of nodes/cores that are used for each workflow run. CWL can do this through the use of embedded JavaScript. However this feature can be awkward to use, does not work with all parameters and also is not fully supported in BEE yet.

Instead of creating multiple workflows with slightly different hard-coded parameters or requiring full support of JavaScript, we utilize Jinja [15] to allow for templating of input workflows. In the BeeSwarm yaml configuration for each scaling test, as can be seen in Fig. 4, template files are listed along with input parameters. Workflows are then generated with Jinja before test execution.

Fig. 4 shows an example configuration for running a single performance test of LULESH [20], an HPC mini-app that we will use later on to test BeeSwarm. A given configuration will include multiple items such as a specification of parameters to pass to the workflow templating step, the base container to build before execution and the input parameters that will be passed upon execution to the workflow.We also include acountoption that determines the number of times a scalability test will be run for result stability.

Fig. 4. Example build configuration for a LULESH performance test.

# *C. Asynchronous Parallel Scaling CI on BEE-Supported Platforms*

Since existing CI environments are typically only allocated a single compute node or virtual machine for running correctness tests, we design BeeSwarm to reserve resources in the Cloud or elsewhere in order to do further testing. BEE supports a number of backends, including cloud APIs such as OpenStack and Google Compute Engine (GCE), as well as native support for HPC systems using Slurm [13] and other batch schedulers, all of which can be configured in a single file. Testing with BEE can also be done asynchronously: developers can make changes, push to a central repository and CI tools will launch the tests. Performance measurements vary from application to application and thus BeeSwarm is designed such that developers can request saving stdout and other text files that are produced by the applications. A generic profiling file is generated after the execution of every workflow.

# *D. Container Build Process*

BeeSwarm makes use of the existing container build interface included in BEE and adds an external component that passes build arguments to the underlying container build tool. Charliecloud [21], an HPC container runtime system, is used as the underlying build tool. Charliecloud includes the ch-image tool which allows for unprivileged building of Dockerfile-based containers. Charliecloud is designed for creating containers that can run on HPC infrastructure, but is also well-suited to cloud and non-HPC environments.

Since our CI scalability tests often require running multiple versions of a single container, each of which may have different build-time requirements, with BeeSwarm we added an extra build-only tool. The BeeSwarm build-only tool is integrated into the scalability test configuration. Each configured test includes a build configuration with a container context directory and a list of build arguments. Before the scalability test is executed, the BeeSwarm component executes a container build task with the given build arguments. Once built, the container is pushed up to the configured registry with a specific testing tag. This allows the integrated BEE build tool to pull down different containers for different scalability tests.

The existing build component within BEE is based on the workflow execution process and the Common Workflow Language (CWL) support for Docker and container runtimes. We utilize the container pulling functionality that is included within this component. Once a container has been built and is stored in a remote registry, a dockerPull requirement within the workflow tells the BEE build component to pull a container from the registry and then prepare it for execution. The component manages all of the required tools within Charliecloud, producing an execution environment that is suitable for the particular scaling test or desired task.

For some of our experiments, notably those with NWChem [22], the container build process is extremely long, due to code complexity and dependency installation. Because of this we had to manually pre-build the containers in a separate CI job and then pre-pull the containers on the host platform. Larger HPC applications may require multiple CI jobs: some jobs would be used for building containers, while later jobs in the pipeline could be used for running correctness tests and or scalability tests.

# *E. Workflows*

BEE was designed to run workflows in the Common Workflow Language (CWL) [12] format, a YAML-based format that includes a series of steps and dependencies between those steps. Steps include a base command field which indicates the command to be run during the step's execution and a number of hints/requirements for the particular step. CWL currently has limited support for MPI in the form of an extension [23]. This adds some support for using different runners such as mpirun with various flags and environment variables. In their example they also use a platform-dependent MPI configuration file. This existing extension, however, does not include more specific options, such as the number of processors/cpus per task and container-specific options, such as the version of MPI that was built in the container or that needs to be bind-mounted in. In order to support a number of these MPI options for our use cases, we implement another BEE-specific extension beeflow:MPIRequirement that is designed to be used with more HPC-specific options, such as cpus_per_task, ntasks, version etc. An example CWL workflow that we use for the CoMD application is shown in Fig. 5. This particular workflow example is designed to run the CoMD application on four nodes (nodes) with 16 MPI tasks in total (ntasks). The input (in) parameters x, y, and z specify the number of unit cells per direction, while i, j, k specify the number of ranks in the corresponding x, y, and z directions. Note that the workflow shown here does no configuration of cloud or HPC resources by itself. These configurations are designed to be placed in separate YAML files as to isolate the workflow from the configuration and

Fig. 5. Example CWL workflow file that was used for running the CoMD application. The DockerRequirement tells the workflow engine to run the application in a specific container (in our case the Charliecloud container runtime is used, even though the requirement name is not changed). We also use the beeflow:MPIRequirement to run CoMD with the available MPI runner.

allow for easily extending one workflow to a different resource setup. This functions as long as the underlying configuration supports a compatible node and task count.

# IV. CASE STUDIES

In this section, we conduct case study experiments to show the parallel scaling performance measuring and tracking capability of BeeSwarm. We chose to run experiments with a number of different HPC applications, including CoMD [24], LULESH [20] and NWChem [22]. These results are designed to show how BeeSwarm could be used with other applications, being adaptable to run different types of containerized workflows with different application metrics. Since each application has slightly different resource requirements, we run each experiment on a slightly different CI/cloud configuration that is best suited to the particular application. With LULESH and CoMD we run tests on the latest version of the repository, while with NWChem we run tests on a number of different commits, since NWChem has a much longer commit history. Throughout this section we will reference a number of different VM instance types that Google Compute Engine provides. See Fig. 6 for the list of node types and their memory amounts.

| Instance Name | CPUs | Memory (GB) |
| --- | --- | --- |
| n1-standard-1 | 1 | 3.75 |
| n1-standard-2 | 2 | 7.50 |
| n1-standard-4 | 4 | ાર |
| n1-standard-8 | 8 | 30 |
| n1-standard-16 | 16 | 60 |
| n1-standard-32 | 32 | 120 |

Fig. 6. List of Google Compute Engine instance types with the number of available CPUs and memory.

![](_page_5_Figure_14.png)

Fig. 7. Strong scaling test of CoMD using 1–16 MPI tasks. This particular test used the n1-standard-16 VM provided by Google Compute Engine. CoMD was run with 80 as the number of unit cells for each dimension and the number of tasks/processors evenly distributed along the dimensions.

# *A. CoMD*

For our first test we decided to run a number of scaling tests using CoMD [24] with BeeSwarm and GitHub Actions. CoMD is a proxy application that can be used for running classical Molecular Dynamics (MD) simulations. We utilized the C version of CoMD and configured tests with the MPI-only version of the code. Also, in this configuration we utilized Google Compute Engine but with a modified cloud configuration that installs a Slurm cluster with an NFS shared file system.

For our first scalability test of CoMD, we utilized a singlenode with 1, 2, 4, 8 and 16 cores. We ran this test on one of Google's n1-standard-16 VMs with 16 cores. Processors were evenly distributed along the dimensions and each dimension was configured with 80 as the number of unit cells. The results for this execution are shown in Fig. 7.

In Fig. 8 we show a scaling test of CoMD on 1, 2 and 4 nodes. Processors were again evenly distributed along the dimensions and dimensions were configured this time with 40 as the number of unit cells. In this particular test we utilized n1-standard-4 VM instances with 4 cores each. These results seem to show rather good scalability for CoMD on multiple nodes.

# *B. LULESH*

We also ran a number of scaling and performance tests on GCE using the Livermore Unstructured Lagrange Explicit Shock Hydrodynamics (LULESH) application [20]. LULESH

![](_page_6_Figure_1.png)

Fig. 8. Strong scaling test of CoMD on 1–4 nodes. The n1-standard-4 VM was used for this test.

![](_page_6_Figure_3.png)

Fig. 9. Results of running LULESH with 1, 8, 27 and 64 MPI tasks on two n1-standard-32 VM instances. LULESH requires that the number of MPI ranks be a cube of an integer. Along the y-axis we have the resulting output value for LULESH in zones per second which gives an application-specific performance measure.

is designed as a proxy application for modeling 3D Lagrangian hydrodynamics problems on unstructured meshes.

For running performance tests with LULESH in the CI environment we built a container with the latest version of LULESH from the GitHub repository.1 For our first test we attempt to focus on measuring only MPI performance, thus during the build process we disable OpenMP. We set up a cloud configuration with two n1-standard-32 nodes available. Since LULESH requires the number of MPI ranks to be the cube of an integer, we execute a test with 1 rank, 8 ranks, 27 ranks and 64 ranks. We run LULESH with a size of 60 and 600 iterations in total. The results of this experiment are shown in Fig. 9. Since as the number of ranks increases, LULESH automatically increases the problem size, execution time is not a good measure of performance. LULESH instead outputs performance in zones per second (z/s).

We also run a second scaling test with an OpenMP-enabled version of LULESH. We set up our cloud cluster configuration with four different Google Compute Engine VM instances: n1 standard-2, n1-standard-4, n1-standard-8 and n1-standard-16. Then we use a modified LULESH workflow to launch four different tests on each of these instances. Since LULESH has OpenMP enabled, it takes advantage of all allocated threads

![](_page_6_Figure_8.png)

Fig. 10. Scaling test of OpenMP version of LULESH on different Google Compute Engine VM instances.

| Commit | Date | Message |
| --- | --- | --- |
| f29685d | Nov 29 2021 | change for singularity [ci skip] |
| 05aafc8 | Dec 9 2021 | Update build simint.sh |
| adab52a | Jan 3 2022 | removed mention of preload script [ci skip] |
| 519b710 | Jan 13 2022 | default memory increased to |
|  |  | 1G |

Fig. 11. Four different commits were chosen from NWChem's recent commit history. This table lists the commit messages and their corresponding dates. Note that these commits are not consecutive. There were around 40 commits between f29685 d and 05aafc8, for instance.

on the system. Only one MPI task was used for each run. The execution times are graphed in Fig. 10.

# *C. NWChem*

NWChem is an HPC tool for running a huge variety of computational chemistry simulations and experiments [22]. Written in Fortran, NWChem can be executed as an MPI job on an HPC or workstation cluster, taking as input a text file that specifies the experiment to be run as well as the various modules that will be used by NWChem. NWChem presents an interesting test case for BeeSwarm since it has an extensive commit history and has an extremely large amount of functionality and subcomponents, all of which can impact scalability and performance over time. Because of NWChem's sheer complexity, depending on the system, the compilation of each container can require up to an hour when built with all modules. This required us to launch a CI job separated from the BeeSwarm CI tests for building the containers, since doing the container build process and then the BeeSwarm tests in the same job could lead to job cancellations caused by going over CI time limits.

For our experiment with NWChem we selected four arbitrary recent commits from the main GitHub repository2 and produced containers for each version of NWChem. We list the commits, their corresponding dates and commit messages in Fig. 11. These span code changes from November 29, 2021 to January 13, 2022.

1https://github.com/LLNL/LULESH

![](_page_7_Figure_1.png)

Fig. 12. Execution of NWChem compiled at four different commits. Commit 05aafc8 gives the shortest execution time, while commit f29685 d, with the longest execution time, lasts for more than 200 seconds longer. Results are the average of two different runs on the same configuration, with variation bars shown.

In Fig. 12 we show results of executing NWChem on an n1-standard-32 node with 8 MPI tasks per node. We decided to use input from the testing directory of the NWChem repository3 which utilizes code from the pspw submodule. The pspw module is used for gamma point calculations for molecules, liquids and other materials [25]. Our results shown here are the average of two runs. Commit f29685 d has an average runtime of about 860 seconds, 05aafc8 of less than 600 seconds, adab52a increases to about 800 seconds and 519b710 goes back down to 750 seconds. Using the output of git diff –numstat we can see that more than 3000 new lines have been added to the Fortran files in the src/nwpw/pspw/ subdirectory between commits f29685 d and 05aafc8. Between commits 05aafc8 and 519b710, no changes are made directly to the pspw module, however, as noted in Fig. 11, global changes, such as the change in default memory, could have had an effect on the results here.

We also ran a single-node scaling test with NWChem on an n1-standard-16 node. For this test we used another input file from the QA subdirectory of NWChem's repository.4 Fig. 13 shows the average of four runs for each commit with MPI tasks numbering 2, 4, 8 and 16 in total. We can see from this particular test, that commit f29685 d seems to show the best scalability out of all of the chosen commit hashes. The results suggest that this particular commit must have some code change that improved the overall scalability for the particular example used. Examining the differences between commit f29685 d and 05aafc8 we note changes in several Fortran files including in src/tce/tce_energy.F and in src/nwpw/band/lib/electron/c_electron.F. The exact line changes do not seem to be related to the SCF input data. However, those same files do reference other scf-named functions and there is a possibility that some of the changes have created a cascading effect giving the results shown here.

![](_page_7_Figure_6.png)

Fig. 13. NWChem scaling on a single n1-standard-16 node with the nwchem/QA/tests/scf_feco5/scf_feco5.nw data set. Error bars included to show variation.

![](_page_7_Figure_8.png)

Fig. 14. NWChem scaling on a single n1-standard-16 with the nwchem/QA/tests/oniom2/oniom2.nw data set. Error bars included to show variation.

This, of course, is not an exact analysis of root causes, which would be better explained by a developer who is more familiar with the inner workings of NWChem and with the best testing configurations.

In Fig. 14 we used the same configuration as in Fig. 13, but with a different input file5 and only two runs instead of four, due to higher runtimes and associated costs. For this particular dataset, the results no longer show good scaling on a single node. From 2 to 4 MPI tasks we see an improvement of around 50 seconds. Then from 4 to 8 tasks we see the total execution time increase by around 10 seconds. Finally from 8 to 16 tasks we can see an increase in time of about 60 seconds. Since this result does not show a large time difference between the different versions, we can conclude that these particular commits did not affect the performance of this particular submodule of NWChem. It's possible that these tests may require more memory for proper scaling than the n1-standard-16 nodes have.

The scaling tests that we do for NWChem here only account for a few of the many modules that the program supports. NWChem is a vast HPC application that can be built with many

5nwchem/QA/tests/oniom2/oniom2.nw

<sup>3</sup>nwchem/QA/tests/pspw_scan_h2o/pspw_scan_h2o.nw 4nwchem/QA/tests/scf_feco5/scf_feco5.nw

| Steps | LULESH | CoMD |
| --- | --- | --- |
| BeeSwarm init time (seconds) | 18.02 | 18.02 |
| Average container | 89.36 | 81.21 |
| build time (seconds) |  |  |
| Average scale | 216.56 | 498.79 |
| test time (seconds) |  |  |
| BEE shutdown time(seconds) | 0.02 | 0.02 |

Fig. 15. Measurements of BeeSwarm initialization time, container build time, scaling test time, for the LULESH OpenMP test and CoMD test. Results are not shown for NWChem since the containers must be pre-built due to long compilation times.

different options and runtime libraries. Running tests on different components are likely to show different results. Modifying the configuration and using different supporting libraries are likely to also reflect changes in scalability and performance experiments.

# *D. BeeSwarm Overhead*

In this section we take a look at the overhead of launching BeeSwarm and the BEE components, as well as other factors such as container build time and execution time. For BeeSwarm's overhead we focus in particular on the initialization time, shutdown time, and the container build time which all factor into the total scaling test time.

Fig. 15 gives the recorded times for two runs of BeeSwarm on Google Compute Engine. One run was recorded when testing LULESH and the other for testing CoMD. After BeeSwarm is set up in the CI environment multiple workflows are executed as scale tests for the particular application. The average time for each of these tests was recorded in the table as *Average scale test time*. These times are highly dependent on the workflow itself and how long the containers take to build. NWChem results were not shown since the containers are not built by BEE, but instead built externally, pushed to a container repository, and then pulled during test time.

In the table we list the BeeSwarm init time which is on average about 18 seconds. This accounts for the launch time of all the components of BEE plus an amount of sleep time to ensure that no applications fail after load. We don't attempt to measure the time needed for configuring the elements in the cloud because this is dependent on the provider used. Internal network issues, provisioning problems or other provider-specific issues could factor into the scaling tests. Given that BEE supports both Google Compute Engine and OpenStack, as well as the possibility of more cloud providers as needs arise, if users require specific cloud configurations or time requirements then they should be able to easily switch to the provider with the desired support.

Another time element we look at is the average container build time, which was around 80–90 seconds for both LULESH and CoMD. The containers we built were based on an existing MPI image and this seems to reduce the time significantly. For more complex containers especially those that require a number of specific dependencies that need to be compiled specifically for the application it is probably best to build a base "dependency" container containing the prebuilt dependencies and then have a secondary container specification that references the first for the final container. Thus if multiple versions of the same application container need to be built, only the application needs to be recompiled and the existing dependencies will already be preinstalled. Another factor that would influence the container build time is the underlying build system. In our case, we rely on Charliecloud's ch-image command to build the containers, but BEE also supports Singularity [26] and may add support for other container tools in the future.

NWChem, on the other hand, is an interesting case since the compilation of all modules can take an extensive amount of time. In this case we don't attempt to build with BeeSwarm, but instead build in a separate CI job. The CI job is designed to build multiple containers in succession and then push these up to Docker Hub [27]. Those same containers can then be pulled down for later scalability tests. Other software projects may need to do something similar, perhaps pushing built containers up to a specialized container registry and then pulling them down for later tests. This may be necessary for larger applications that can take longer periods of time to compile.

# V. DISCUSSION

We introduced BeeSwarm as a tool to allow scalability and performance testing of container-based applications in CI. We also show the techniques and the methods for doing future scalability results of HPC applications and workflows. As applications change from commit to commit, CI tools like BeeSwarm can be extremely useful to ensure both code quality and code performance. Our experiments show that in complex applications, performance can vary from one module or component to another. On large HPC projects, like NWChem, CI testing can be utilized to measure performance changes between different software components as major changes are merged into the repository. On the typical project, scalability testing would probably be done on merging of major changes into a main branch, and or upon release of new software versions. Other tests could also be run at the developers discretion when working with a performance critical section of code. Smaller projects may not benefit from extensive CI performance testing since code changes may be minor and performance testing may be easier and less costly to run locally.

As for future research directions, there are a number of areas where further testing could be done and where BeeSwarmcould be improved. Currently, BeeSwarm utilizes only cloud configurations for testing, but BEE also has good support for HPC systems running Slurm and IBM LSF. Comparisons between running scaling tests in the cloud and on existing HPC systems could be useful for HPC scaling tests. Results run on HPC systems may also give more accurate scaling results, since they may more accurately portray the final system that an application is designed to run on. Of course, the main goal of BeeSwarm is to detect changes in performance from one version of an application to another during the software development process. While performance in the cloud will certainly not be the same as performance on an HPC system, the relative performance differences in cloud systems should be useful indicators of performance problems, thus helping to catch these issues before they even run on an HPC system. However, one must be careful when choosing cloud systems for scalability tests; shared instances, for example, may cause problems with result stability and give inaccurate performance indications.

Our custom MPI requirement extension to CWL could also be improved. We would like to conform to standard CWL as much as possible, and in fact there is an existingMPI extension requirement proposed by the CWL creators. However, this existing MPI extension is not completely usable for HPC; the standard MPI requirement works by storing host-specific execution information in a separate yaml file that is then passed to the orchestration tool through a command-line parameter. While this method works for small examples and with Singularity-based containers, it will fail for workflows with multiple MPI-based steps, since the extension applies options at a global workflow level and each MPI step may require slightly different options, perhaps due to the container used, or even if the system is different for each step. Because of these issues, we decided to write our workflows with our own beeflow:MPIRequirement. In the future we would like to contribute requirement improvements back to the CWL community and also attempt to use a more standardized requirement that is more flexible for the needs of HPC.

The configuration and management of BeeSwarm could also be improved in a number of ways for general usability. Currently cloud launches are designed to be manually terminated after set up, which is done to allow for easy debugging of issues that could occur during a scaling test. In some cases we may want to log into a system with a failing test in order to examine the environment and the generated output. However for realworld applications, manually shutting down a cloud cluster is not feasible, and if forgotten about could lead to added costs. More work should be done to determine the best way to take snapshots of the application runs, their environments and other aspects in order to keep enough information for debugging purposes, while avoiding the hassle of manually deprovisioning resources in the cloud.

One aspect of cloud-scalability testing that can be prohibitive is the cost of using cloud-based resources. For long running jobs in the cloud, costs can run very high for applications, and developers will want to ensure that time and resources are not wasted. Depending on the size of the application and the tests to be run, developers will want to limit how often scalability tests are run. In some cases developers may be able to manually execute scalability tests using BeeSwarm, knowing that costs will not be high. In many cases, however, using tools such as BeeSwarm will likely save on costs that would be incurred by performance problems found during production usage. BeeSwarm will catch these issues early and lead to smoother releases and less time spent on bug-fixing.

# VI. RELATED WORK

Many projects have built parallel scaling test tools to facilitate HPC application development. Most of these must be configured manually and expect some sort of underlying support for resource management and configuration. For example, Vetter and Chambreau [28] proposed a profiling library for MPI applications, which is only based on statistical information about MPI functions. The solution is light-weight, MPI task-local and does not add as much overhead as other similar tools.

LDMS [29] launches a large scale monitoring system to dynamically trace network traffic, file system statistics, CPU loads and memory usages at runtime. LDMS is able to capture whole system state information all while remaining non-intrusive. The tool can help developers find bottlenecks in HPC applications which could be caused by a wide range of factors.

There are many parallel analysis tools that have been proposed as well. Chen and Sun [30] proposed an effective parallel scaling testing and analysis system – STAS. Chung et al. [31] proposed a configurable MPI parallel scaling analysis tool for the Blue Gene/L supercomputer. Brunst and Weber [32] proposed a performance tool, Vampir, that can be used to detect hot spots in HPC applications. This can efficiently help HPC developers make their applications more scalable. Merchant and Prabhakar[33] proposed JACE (Job Auto-creator and Executor), a tool that enables automation of creation and execution of complex performance and scalability regression tests. It can help developers tune an application on a given platform to maximize performance given different optimization flags and tunable variables.

Muraleedharan [34] presented an HPC performance and scalability test tool, Hawk-i, that uses cloud computing platforms to test HPC applications in order to reduce the effort to access relative scarce and on-demand high performance resources. Bell et al.[35] proposed, ParaProf, a portable, extensible, and scalable tool for parallel performance profile analysis. It gathers hardware counters and traceable information in order to offer much more detailed profiling results similar to state-of-the-art single process profiling tools. Yoo et al. [36] proposed a parallel scaling test tool, PATHA, that uses system logs to extract performance measures and apply the statistical tools and data mining methods on the performance data to identify bottlenecks or to debug the performance issues in HPC applications.

Various CI performance solutions have been proposed and analyzed. Waller et al. [37] take a look at how performance can be added to CI. Other more recent research focused on microbenchmarking for Java and Go-based applications [38]. The popular Jenkins[39] CI tool has a performance analysis plugin [5]. Other language-dependent solutions, such as PerfCI [6] which is used for Python projects, have been proposed to handle CI. Other solutions have been proposed for web and general applications, such as BlazeMeter[4]. BlazeMeter is an enterprise CI solution that claims to be able to run performance tests against a variety of application types and platforms. Platforms supported include many of the major Cloud Providers, such as Google and AWS, all while using Docker for containerization. These recent works allow for performance testing for general applications but they do not handle the need for scalability testing, where tests need to be scaled on a number of compute resources, and they don't have any support for provisioning HPC-like resources for testing. They also have limited support for HPC-specific container runtimes like Charliecloud [21] and Singularity [26]. There is also no support for components of the Extreme-Scale Scientific Software Stack (E4S) [40], which attempts to provide frameworks for running scientific applications in a portable manner with containers.

There has also been a lot of research into using Cloud systems and Infrastructure-as-a-Service (IaaS) for HPC and scientific applications in general. Castro et al. [41] and other researchers have argued that while cloud computing can improve the capacity and management problems associated with dedicated HPC, moving software into the cloud introduces other management and configuration issues that can be difficult for end-users to handle. Solutions to this problem include providing Software-asa-Service (SaaS) and Platform-as-a-Service (PaaS) options that are specific to HPC. Some cloud providers have begun to implement batch processing and to offer other HPC-related tools, such as AWS Batch [42]. However, in many cases the solutions that are currently offered by many cloud providers are not usable for HPC applications that rely on specific configurations and container runtime systems. For our research, instead, we utilize custom cloud configurations that can be tweaked as needed.

NWChem, one of the main applications we used in this work, has been studied by a number of different publications, including by Si et al. [43] and Aprà et al. [44]. Multiple versions of the CoMD application, using OpenMP, OpenCL and other vendor-specific models, have also been extensively tested and compared [45]. Karlin et al. [46] include scaling test results for LULESH with a variety of programming models. Updated tests and results for LULESH version 2.0 have also been studied [47]. LULESH itself has also been implemented using a number of different programming languages and models [48].

There are many workflow orchestration systems that have been designed for the cloud and for HPC systems, including StreamFlow, Mashup and BEE. StreamFlow [49] attempts to allow workflows to utilize multiple underlying systems, both in the cloud and in HPC centers, by abstracting system interfaces and resource specifications. Mashup [50] takes a slightly different direction by making use of serverless cloud interfaces, which are not commonly used for HPC applications since they often require libraries that are highly optimized for the hardware. BEE [7], which our work is based on, is a workflow orchestration system designed for running HPC applications in both the cloud and on HPC resources. Existing research with BEE [51] has looked at running workflows across multiple systems, which is similar to StreamFlow except that BEE takes different approaches to workflow storage, execution and scheduling. As far as we know, there have not been any existing workflow systems, or extensions there of, to specifically support scalability testing for HPC.

# VII. CONCLUSION

Our work shows the importance of performance and scalability testing for HPC applications, as well as the need for a CI system to do just that. We design BeeSwarm to provide asynchronous performance and scalability testing for HPC applications using CI, making use of cloud resources to set up systems to run the scalability tests. Experiments done with GitHub Actions using Google Compute Engine as a compute backend, show that BeeSwarm can be used in several different scenarios for CI scalability testing. Experiments done with LULESH and CoMD show how scalability can be measured for a variety of HPC applications. Our results with NWChem also show how scalability testing can be done for multiple versions of a repository, letting developers see performance changes over time as they make changes to large code bases. BeeSwarm has good support for most scientific applications, since it is based on BEE, thus making it easier for HPC application developers to set up scalability testing and then use results to help guide their work.

# REFERENCES

- [1] M. Fowler and M. Foemmel, "Continuous integration," *Thought-Works*, 2006. [Online]. Available: http://www.thoughtworks.com/ ContinuousIntegration.pdf
- [2] M. Bauer, S. Treichler, E. Slaughter, and A. Aiken, "Legion: Expressing locality and independence with logical regions," in *Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal.*, 2012, Art. no. 66.
- [3] C. R. Ferenbaugh, "PENNANT: An unstructured mesh mini-app for advanced architecture research," *Concurrency Computation: Pract. Experience*, vol. 27, no. 17, pp. 4555–4572, 2015.
- [4] BlazeMeter, "Performance testing, validate performance at scale," 2021. [Online]. Available: https://www.blazemeter.com/product/performancetesting
- [5] Performance-plugin, 2021. [Online]. Available: http://jenkinsci.github.io/ performance-plugin/RunTests.html
- [6] O. Javed et al., "PerfCI: A toolchain for automated performance testing during continuous integration of python projects," in*Proc. 35th IEEE/ACM Int. Conf. Automated Softw. Eng.*, 2020, pp. 1344–1348. [Online]. Available: https://doi.org/10.1145/3324884.3415288
- [7] J. Chen et al., "Docker-enabled build and execution environment (BEE): An encapsulated environment enabling HPC applications running everywhere," 2017, *arXiv: 1712.06790*.
- [8] J. Tronge et al., "BeeSwarm: Enabling parallel scaling performance measurement in continuous integration for HPC applications," in *Proc. 36th IEEE/ACM Int. Conf. Automated Softw. Eng.*, 2021, pp. 1136–1140.
- [9] I. GitHub, "Github actions," 2021. [Online]. Available: https://docs.github. com/en/actions
- [10] J. Chen et al., "BeeFlow: A workflow management system for in situ processing across HPC and cloud systems," in *Proc. 38th IEEE Int. Conf. Distrib. Comput. Syst.*, 2018, pp. 1029–1038.
- [11] J. Chen et al., "Build and execution environment (BEE): An encapsulated environment enabling HPC applications running everywhere," in *Proc. IEEE Int. Conf. Big Data*, 2018, pp. 1737–1746.
- [12] P. Amstutz et al., "Common workflow language, v1.0. specification, common workflow language working group," 2016. [Online]. Available: https://w3id.org/cwl/v1.0/
- [13] SchedMD, "Slurm workload manager," 2020. [Online]. Available: https: //slurm.schedmd.com/
- [14] IBM, "IBM spectrum LSF suites," 2021. [Online]. Available: https://www. ibm.com/products/hpc-workload-management
- [15] Pallets, "Jinja," 2007. [Online]. Available: https://jinja.palletsprojects. com/en/3.0.x/
- [16] Google, "Compute engine: Virtual machines (VMS)," 2021. [Online]. Available: https://cloud.google.com/compute
- [17] O. Foundation, "Open source cloud computing infrastructure Open-Stack," 2021. [Online]. Available: https://www.openstack.org/
- [18] X. Li, "Scalability: Strong and weak scaling," 2018. [Online]. Available: https://www.kth.se/blogs/pdc/2018/11/scalability-strong-andweak-scaling/
- [19] I Karlin, J. Keasler, and J. R. Neely, "LULESH 2.0 Updates and Changes," Jul. 2013, doi: 10.2172/1090032.
- [20] I. Karlin, J. Keasler, and R. Neely, "LULESH 2.0 updates and changes," Lawrence Livermore Nat. Lab. (LLNL), Livermore, CA, USA, Tech. Rep. LLNL-TR-641973, Aug. 2013.

- [21] R. Priedhorsky and T. Randles, "CharlieCloud: Unprivileged containers for user-defined software stacks in HPC," in *Proc. Int. Conf. High Perform. Comput., Netw. Storage Anal.*, 2017, Art. no. 36.
- [22] M. Valiev et al., "NWChem: A comprehensive and scalable open-source solution for large scale molecular simulations," *Comput. Phys. Commun.*, vol. 181, no. 9, pp. 1477–1489, 2010. [Online]. Available: https://www. sciencedirect.com/science/article/pii/S0010465510001438
- [23] R. W. Nash, M. R. Crusoe, M. Kontak, and N. Brown, "Supercomputing with MPI meets the common workflow language standards: An experience report," in *Proc. IEEE/ACM Workflows Support Large-Scale Sci.*, 2020, pp. 17–24. [Online]. Available: http://dx.doi.org/10.1109/WORKS51914. 2020.00008
- [24] E. C.-D. C. for Materials in Extreme Environments, "Classical molecular dynamics proxy application," 2016. [Online]. Available: https://github. com/ECP-copa/CoMD
- [25] E. J. Bylaska, "Pseudopotential plane-wave density functional theory (NWPW)," 2021. [Online]. Available: https://nwchemgit.github.io/Plane-Wave-Density-Functional-Theory.html#pspw-tasks---gamma-pointcalculations
- [26] Sylabs.io, "Singularity," 2021. [Online]. Available: https://sylabs.io/
- [27] D. Inc., "Docker hub," 2022. [Online]. Available: https://hub.docker.com/ [28] J. Vetter and C. Chambreau, "mpiP: Lightweight, scalable MPI profiling,"
- *URL: http://www. llnl. gov/CASC/mpiP*, Jan. 2005. [29] A. Agelastos et al., "The lightweight distributed metric service: A scalable infrastructure for continuous monitoring of large scale computing systems and applications," in *Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal.*, 2014, pp. 154–165.
- [30] Y. Chen and X.-H. Sun, "STAS: A scalability testing and analysis system," in *Proc. IEEE Int. Conf. Cluster Comput.*, 2006, pp. 1–10.
- [31] I.-H. Chung, R. E. Walkup, H.-F. Wen, and H. Yu, "MPI performance analysis tools on blue Gene/L," in*Proc. ACM/IEEE Conf. Supercomputing*, 2006, pp. 16–16.
- [32] H. Brunst and M. Weber, "Custom hot spot analysis of HPC software with the Vampir performance tool suite," in *Proc. 6th Int. Conf. Tools High Perform. Comput.*, Springer, 2013, pp. 95–114.
- [33] S. Merchant and G. Prabhakar, "Tool for performance tuning and regression analyses of HPC systems and applications," in *Proc. 19th Int. Conf. High Perform. Comput.*, 2012, pp. 1–6.
- [34] V. Muraleedharan, "Hawk-i HPC cloud benchmark tool," University of Edinburgh, Edinburgh, 2012.
- [35] R. Bell, A. D. Malony, and S. Shende, "ParaProf: A portable, extensible, and scalable tool for parallel performance profile analysis," in *Proc. Eur. Conf. Parallel Process.*, Springer, 2003, pp. 17–26.
- [36] W. Yoo, M. Koo, Y. Cao, A. Sim, P. Nugent, and K. Wu, "PATHA: Performance analysis tool for HPC applications," in *Proc. IEEE 34th Int. Perform. Comput. Commun. Conf.*, 2015, pp. 1–8.
- [37] J. Waller, N. C. Ehmke, and W. Hasselbring, "Including performance benchmarks into continuous integration to enable DevOps," *SIGSOFT Softw. Eng. Notes*, vol. 40, no. 2, pp. 1–4, Apr. 2015. [Online]. Available: https://doi.org/10.1145/2735399.2735416
- [38] C. Laaber and P. Leitner, "An evaluation of open-source software microbenchmark suites for continuous performance assessment," in *Proc. 15th Int. Conf. Mining Softw. Repositories*, 2018, pp. 119–130. [Online]. Available: https://doi.org/10.1145/3196398.3196407
- [39] Jenkins, 2021. [Online]. Available: https://www.jenkins.io/
- [40] E. Project, "The extreme-scale scientific software stack," 2021, [Online]. Available: https://e4s-project.github.io/index.html
- [41] H. Castro, M. Villamizar, O. Garcés, J. Pérez, R. Caliz, and P. F. P. Arteaga, "Facilitating the execution of HPC workloads in colombia through the integration of a private IaaS and a scientific PaaS/SaaS marketplace," in *Proc. 16th IEEE/ACM Int. Symp. Cluster Cloud Grid Comput.*, 2016, pp. 693–700. [Online]. Available: https://doi.org/10.1109/CCGrid.2016. 52
- [42] A. W. Services, "AWS batch," 2022. [Online]. Available: https://aws. amazon.com/batch/
- [43] M. Si, A. J. Peña, J. Hammond, P. Balaji, and Y. Ishikawa, "Scaling NWChem with efficient and portable asynchronous communication inMPI RMA," in *Proc. 15th IEEE/ACM Int. Symp. Cluster Cloud Grid Comput.*, 2015, pp. 811–816.
- [44] E. Aprà, M. Klemm, and K. Kowalski, "Efficient implementation of manybody quantum chemical methods on the Intel Xeon Phi coprocessor," in *Proc. Int. Conf. High Perform. Comput. Netw. Storage Anal.*, 2014, pp. 674–684.
- [45] ExMatEx, "CoMD Proxy Application," 2012. [Online]. Available: http: //www.exmatex.org/comd.html

- [46] I. Karlin et al., "Exploring traditional and emerging parallel programming models using a proxy application," 2021. [Online]. Available: https://cs. stanford.edu/zdevito/Programming_Model_Comparison.pdf
- [47] I. Karlin, J. Keasler, and R. Neely, "LULESH 2.0 updates and changes," 2013. [Online]. Available: https://asc.llnl.gov/sites/asc/files/2021--01/ lulesh2.0_changes1.pdf
- [48] Lawrence Livermore National Laboratory, "LULESH | Advanced Simulation and Computing," 2013. [Online]. Available: https://asc.llnl.gov/ codes/proxy-apps/lulesh
- [49] I. Colonnelli, B. Cantalupo, I. Merelli, and M. Aldinucci, "StreamFlow: Cross-breeding cloud with HPC," 2020, *arXiv: 2002.01558*, [Online]. Available: https://arxiv.org/abs/2002.01558
- [50] R. B. Roy, T. Patel, V. Gadepally, and D. Tiwari, "Mashup: Making serverless computing useful for HPC workflows via hybrid execution," in *Proc. 27th ACM SIGPLAN Symp. Princ. Pract. Parallel Program.*, 2022, pp. 46–60. [Online]. Available: https://doi.org/10.1145/3503221.3508407
- [51] J. Tronge et al., "BEE orchestrator: Running complex scientific workflows on multiple systems," in *Proc. IEEE 28th Int. Conf. High Perform. Comput. Data Analytics*, 2021, pp. 376–381.

![](_page_11_Picture_31.png)

**Jake Tronge** received the MS degree in computer science from Kent State University, in 2022. He is a post masters intern with Los Alamos National Laboratory. His research interests include HPC workflow orchestration, parallel programming models, and natural language processing.

![](_page_11_Picture_33.png)

**Jieyang Chen** received the master's and PhD degrees in computer science from the University of California, Riverside, in 2014 and 2019, respectively. He is an assistant professor with the Department of Computer Science, University of Alabama at Birmingham. His research interests include high performance computing, parallel and distributed systems, and Big Data analytics.

![](_page_11_Picture_35.png)

**Patricia Grubel** is a staff scientist with Future Architectures and Applications Team, Los Alamos National Laboratory. Her current work includes orchestration of scientific workflows for reproducibility, reliability and provenance, software engineering for sustainability and reliability, and profiling scientific applications on new architectures.

![](_page_11_Picture_37.png)

**Tim Randles**is the advanced simulation and computing computational systems and software environment program manager with Los Alamos National Laboratory. He has been working in scientific, research and high performance computing for more than 20 years. His current work is focused on deploying new computation platforms into production at LANL and the convergence of the high performance and cloud computing worlds, specifically leveraging cloud computing software and methods to enhance the flexibility and usability of world-class supercomputers.

![](_page_12_Picture_1.png)

**Rusty Davis** is a staff scientist working on resilience and virtualization. He attended Clemson University majoring in computer science studying the intersection of resilience and energy efficiency. His research interests include machine learning, workflows, and containerization.

![](_page_12_Picture_3.png)

**Steven Anaya** received the BS degree in computer science and the BS degree in mathematics from the New Mexico Institute of Mining and Technology, Socorro, NM, in 2021. He is currently working toward the MS degree in computational linguistics with the University of Washington, Seattle, WA. He continues to work on the BEE project as well as the Active Learning Framework (ALF) for training machine learning potentials for atomistic simulations. His primary research interests include large language model (LLM) translation technologies and machine learning for scientific applications.

![](_page_12_Picture_5.png)

**Quincy Wofford** is a staff scientist with Los Alamos National Laboratory in the Applied Computer Science (CCS-7) Group. He is currently building automated deployment mechanisms for distributed applications on HPC systems.

![](_page_12_Picture_7.png)

**Qiang Guan** is an assistant professor with the Department of Computer Science, Kent State University, Kent, Ohio. He is the direct of Green Ubiquitous Autonomous Networking System Lab (GUANS). He is also a member of Brain Health Research Institute (BHRI), Kent State University. He was a computer scientist in data science with Scale Team, Los Alamos National Laboratory before joining KSU. His current research interests include fault tolerance design for HPC applications; HPC-Cloud hybrid system; virtual reality; quantum computing systems and applications.

