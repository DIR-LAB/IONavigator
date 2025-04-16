# A Failure Recovery Solution for Transplanting High-Performance Data-Intensive Algorithms from the Cluster to the Cloud

Da-Qi Ren1 , Zane Wei 2 The US R&D Center, Huawei Technologies 2330 Central Expressway, Santa Clara, CA 95050, USA Email: 1 daqi.ren@huawei.com, 2 weizhulin@huawei.com

 *Abstract* **—The computing-cloud manages huge numbers of virtualized resources to provide uniquely beneficial computing paradigms for scientific research. A modern cloud can behave in a virtual context - much like a local homogeneous computer cluster - to deliver High Performance Computing (HPC) platforms that provide public users with access, cut purchase costs, and eliminate the maintenance burden of sophisticated hardware. For decades most distributed scientific computing software has been designed to run on clusters. Research on how to transplant cluster-based programs and performance-tuning mechanisms onto the cloud platform has gathered momentum in recent years. This paper introduces a fault tolerant approach that assures the reliability virtual clusters on clouds where high–performance and data-intensive computing paradigms are deployed. We have solved the failure recovery issue for TCP connections containing MPI error handlers by exploiting and modeling the constraints of low-level distributed resources. The combined MPI and TCP environment can support software development for multiple parallel programming models, including asynchronous distributed computing based on MPI for scientific HPC and synchronous distributed computing for big data, such as MapReduce and Pregal. This paper sets out detailed MPI/TCP fault-tolerant mechanisms, including primitives and functions. These elements enable the systematic and hierarchical development of a globally optimized HPC on the cloud platform.** 

 *Keywords — High-Performance Computing; Data-Intensive Computing; Cloud Computing; Fault Tolerance.* 

#### I. INTRODUCTION

High-performance computing (HPC) provides accurate and rapid solutions for scientific and engineering problems based on powerful computing engines and the highly parallelized management of computing resources. Cloud computing as a technology and paradigm for the new HPC era is set to become one of the mainstream choices for high-performance computing customers and service providers. [1] [2] The cloud offers end users a variety of services covering the entire computing stack of hardware, software, and applications. Charges can be levied on a pay-per-use basis, and technicians can scale their computing infrastructures up or down in line with application requirements and budgets. Cloud computing technologies provide easy access to distributed infrastructures and enable customized execution environments to be easily established. The computing cloud allows users to immediately access required resources without capacity planning and freely release resources that are no longer needed. [1] [3]

Each cloud can support HPC with virtualized Infrastructure as a Service (IaaS). IaaS is managed by a cloud provider that enables external customers to deploy and execute applications. Fig.1 shows the layer correspondences between cluster computing and cloud computing models. The main challenges facing HPC-based clouds are cloud interconnection speeds and the noise of virtualized operating systems. [4] Technical problems include system virtualization, task submission, cloud data I/O, security, and

![](_page_0_Figure_9.png)

Fig.1 Layer correspondences between cluster computing and cloud computing.

![](_page_0_Picture_13.png)

reliability. HPC applications require considerable computing power, high performance interconnections, and rapid connectivity for storage or file systems, such as supercomputers that commonly use infiniband and proprietary interconnections. However, most clouds are built around heterogeneous distributed systems connected by lowperformance interconnection mechanisms, such as 10-Gigabit Ethernet, which do not offer optimal environments for HPC applications. Tab.1 shows the comparison of technical characters between cluster computing and cloud computing models. [4] [5]. The differences in infrastructures between cluster computing and cloud computing have increased the need to develop and deploy fault tolerance solutions on cloud computers.

### II. FAILURE MODEL FOR HPC ON CLOUD

An HPC cloud platform provides a comprehensive set of integrated cloud management capabilities to meet users' HPC requirements. Deployed on top of a HPC cloud, the software manages the running of computing and data-intensive distributed applications on a scalable shared grid, and accelerates parallel applications to accelerate results and improve the utilization of available resources. An HPC cloud enables the self-service creation and management of multiple flexible clusters to deliver the performance required by computing-intensive workloads in multitenant HPC environments. This paper demonstrates our failure recovery approach using a typical MPI/TCP model.

#### A. *HPC Fault Tolerant Model on Cloud*

 MPI provides a message-passing application programmer interface and supports both point-to-point and collective communication. MPI has remained the dominant model used for HPC for several decades due to its high performance, scalability, and portability.

Many of the current big data applications use RPC to establish TCP connections for high-performance dataintensive computing. Typical examples such as MapReduce [6] and Pregel [7] require long TCP connections to build up virtual cluster networks over the Internet or cloud. Hadoop RPC forms the primary communication mechanism between the nodes in the Hadoop cluster. HDFS is the Hadoop Distributed File System that enables multiple machines to implement functions. [8] Hadoop NameNode receives requests from HDFS clients in the form of Hadoop RPC requests over a TCP connection. The listener object listens to the TCP port that serves RPC requests from the client. [9]

In comparison, GraphLab simultaneously uses MPI and TCP, and simplifies the update process because users do not need to explicitly define the information flow from Map to Reduce and can just modify data in-place. For iterative computations, GraphLab's knowledge of the dependency structure directly communicates modified data to the destination. GraphLab presents a simpler API and data graph to programmers, and informs GraphLab of the program's communication needs. This implementation model uses

![](_page_1_Figure_7.png)

Fig.2 Three IaaS layers from bottom to top: cloud resources and TCP networks; hosts and virtual machines; guest MPI applications.

|  | Cloud Computing | Cluster Computing |
| --- | --- | --- |
| Performance | 1. Computation cost | 1. Computation cost |
| factors | 2. Storage cost | 2. Communication latencies |
|  | 3. Data transfer cost (in or out for | 3. Data dependencies |
|  | each service | 4. Synchronization |
| Performance | 1. Specifying a particular service | 1.Defining the data size to be |
| Tuning | for a particular task; | distributed |
|  | 2. Archiving intermediate data on | 2.Scheduling the send and |
|  |  | receive workload |
|  | a particular storage device; | 3.Task synchronization |
|  | 3. Choosing a set of locations for |  |
|  | input and output data. |  |
| Fault | 1. Resend | 1.Checkpointing protocols |
| Tolerance | 2. Reroute | 2.Membership protocol |
|  | 3. graph scheduling | 3.System synchronization |
|  | 4. QoS |  |
| Goal | Minimizing the total cost of | Minimizing the total |
|  | execution while meeting all the | execution time; performing |
|  | user-specified constraints. | on users’ hardware platforms. |
| Reliability | No | Yes |
| Task size | Single large | Small and medium |
| Scalable | No | Yes |
| Switching | Low | High |
| Application | HPC, HTC | SME interactive |

Tab.1 Comparison of performance factors and tuning in cloud and cluster computing models.

collective synchronous MPI operations for communication. [10]

Based on the applications listed above, we have modeled a three-layer IaaS platform, which, from bottom to top, are: cloud resources and TCP networks; hosts and virtual machines; and guest MPI applications. The cloud provider is responsible for administering services and cloud resources, such as hardware and virtual machines, that customers use to deploy and execute applications. Fig.2 summarizes the vertical cloud architecture and the scope of each cloud participant. We have identified three types of failure in a cloud platform: hardware/network failure, virtual machine failure, and application failure. Each of the above layers has exclusive fault tolerant functions; however, for optimal performance, collaborative failure management approaches including best effort must be considered. [11]

#### *B. Failure detection*

 At the application level, MPI fault tolerance or virtual machine sensors can detect an application or virtual machine failure. Both the application and virtual machine layers must collaborate to precisely locate errors. Errors can have three origins: MPI application, the virtual machine, and TCP network/hardware.

 At the network/hardware level, TCP connections can be long-term as certain users maintain connections for hours or even days at a time. The duration of TCP connections provides an excellent parallel platform for a group of virtual machines to run like a cluster on a cloud. If a problem occurs, heartbeating can check whether the network connection is alive because a connected network periodically sends small packets of data (heartbeats). If the peer does not receive a heartbeat for a specified time period, the connection is considered broken. However, the TCP protocol does not provide heartbeats and TCP endpoints are not notified of broken connections, causing them to live indefinitely, forever trying to communicate with the inaccessible peer. Higher level applications must then reinitialize certain applications. For many scientific computing applications, especially those with high-availability requirements, this missing failure notification is a critical issue that urgently requires a recovery mechanism.

## C. *Failure Recovery*

 If an error originates from the program at the application layer, the program itself should be able to self-recover, e.g. the map-reduce implementation replicates data on the HDFS. If a node fails, tasks that are using the data on the failed node can restart on another node that hosts a replica of the data.

 If an error occurs on a virtual machine due to a hardware host failure, the cloud administration starts a new virtual machine with the same features, allowing users to redeploy tasks and restart and synchronize the new machine. In line with an application's properties, the checkpointing and recovery process is required after a new virtual machine is generated. The checkpointing process periodically takes system snapshots and stores application status information in persistent storage units. If a failure occurs, the most recent status can be retrieved and the system recovered. Userdirected checkpointing requires the application programmer to form the checkpoint and write out any data needed to restart the application. Checkpoints must be saved to persistent storage units, which are typically cloud-based, that will not be affected by the failure of a computing element; however, there are two disadvantages in this scenario: first, the user is responsible for ensuring that all data is saved; second, the checkpoints must be taken at particular points in the program.

#### Algorithm: MPI setup RPC call.

|  | /*MPI initialization communicator group */ |
| --- | --- |
| 1 | MPI_INIT; MPI_COMM_WORLD = nprocs; |
|  | /* MPI process to Create communicators*/ |
| 2 | MPI_COMM_SIZE(MPI_COMM_WORLD, |
|  | &mpi_size); |
| 3 | MPI_Gather ( IPAddess, Machines); |
|  | /* Gther node informations*/ |
|  | /*Create parameter table using information from |
|  | MPI*/ |
|  | /* Performs RPC call to the target machine in |
|  | Hadoop Cluster.* / |
| 4 | FOR ( size_t; i=1; i<nprocs; i++) { |
| 5 | Listen (); |
| 6 | } |
| 7 | FOR ( size_t; i = 0; i< nprocs; i++ ) { |
| 8 | Connect (i); |
| 9 | } |
|  | /* Establish TCP connection with RPC; |
|  | 10 In_thread_num = machine_num /proc_per_thread; |
|  | 11 Out_thread_num = machine_num/proc_per_thread; |
|  | /* Create TCP long connections over the virtual |
|  | machines identified by MPI communicators*/ |
|  | /* Run distributed computing over the TCP |
|  | connection*/ |

Fig.3 Steps for setting up a TCP connection using MPI initialization. The pseudo-code describes how MPI and TCP jointly build a Hadoop cluster.

# D. *Related Works on the Fault Tolerence MPI*

 Some research has been conducted into running MPI applications on cloud infrastructures with checkpointing and recovery techniques in place. The MPI Forum's Fault Tolerance Working Group has defined a set of semantics and interfaces to enable fault tolerant applications and libraries to be portably constructed on top of the MPI interface. [12] The run-through stabilization component of the proposal [13] enables applications to continue running and using MPI if one or multiple processes in the MPI universe fail. The proposal assumes the fail-stop process failure function that permanently stops a crashed process. Proposal [13] discusses how MPI implementation should handle transient failures. Other types of faults not currently addressed by the MPI standard (that is, reliable message delivery) such as Byzantine failures [14] are left for the application to address as necessary.

Algorithm: MPI error handler setup, the main function.

```
1 int i, myrank, ini_size, curr_size; 
2 MPI_Comm worker_comm [MAX_WORKERS]; 
3 MPI_Comm_rank (MPI_COMM_WORLD, 
4 &myrank ); 
5 MPI_Comm_size ( MPI_COMM_WORLD, &ini_size ); 
6 curr_size = ini_size; 
7 /* create intercommunicators, set error handlers */ 
8 for ( i = 1; i< curr_size; ++i ) 
9 { 
10 MPI_Intercomm_Create ( MPI_COMM_SELF, 0, 
11 MPI_COMM_WORLD, i, 
12 IC_CREATE_TAG, &worker_comm[i-1] 
13 ); 
14 MPI_Comm_Set_Errhandler( worker_comm[i-1], 
15 MPI_ERRORS_RETURN ); 
16 } 
17 If (TCP application) { 
18 Don't do anything if the application is TCP based;*/
19 } 
20 If (MPI Application){ 
21 manage MPI higher level fault tolerant mechanisms 
22 } 
23 For ( i = 1; i< curr_size; ++i ) {
24 MPI_Comm_free( &worker_comm[i-1] ); 
25 MPI_Finalize( ); 
26 }
```
 Fig.4 MPI error handler setup, and the main function.

III. MPI/TCP INFORASTRUCTURE WHEN SEVERING HIGH-PERFORMANCE DATA-INTENSIVE COMPUTING ON CLOUD

This paper proposes a method to add failure recovery capabilities to a cloud environment for scientic HPC applications. An HPC application with MPI implementation is able to extend the class of MPI programs to embed the HPC application with various degrees of fault tolerance. An MPI FT mechanism can realize a recover-and-continue solution; if an error occurs, only failed processes re-spawn, the remaining living processes remain in their original processors/nodes, and system recovery costs are thus minimized.

#### A. *MPI and TCP*

 Users can initialize a low-level MPI/TCP communication model by enabling the communication group to use the MPI_COMM to collect distributed system data, and then deliver it to the RCP to create a long-term TCP connection. Executing a distributed application over TCP connections and on a virtual cluster involves a similar process that requires three steps: 1) Initialize communicator groups using MPI; 2) Pass the data to RCP; 3) All devices with TCP connections complete connection setup and enter the established state. TCP software can then operate normally. Fig. 3 shows the steps and pseudo-code.

Algorithm: MPI spawn new communicators.

| 1 | MPI_Comm Cgr = MPI_COMM_WORLD; |
| --- | --- |
| 2 | int get_current_state() { |
| 3 | MPI_Rank_info irs; |
| 4 | int deadnode =0; |
| 5 | for ( n = 0; n < curr_size; ++n ) { |
| 6 | /* Try to validate the status of each MPI rank, |
| 7 | find out who is dead, and how many new nodes |
| 8 | are needed ;*/ |
| 9 | MPI_Comm_validate_rank(Cgr, n, rs); |
| 10 | If ( MPI_RANK_OK != rs.state ) { |
| 11 | return n; |
| 12 | deadnode++; } |
| 13 | } |
| 14 | int NUM_SPAWNS = deadnode; |
| 15 | int errcodes[NUM_SPAWNS]; |
| 16 | MPI_Comm parentcomm, intercomm; |
| 17 | MPI_Comm_get_parent( &parentcomm ); |
| 18 | if (parentcomm == Cgr) { |
| 19 | MPI_Comm_spawn ( "Exe", |
| 20 | MPI_ARGV_NULL, |
| 21 | np, MPI_INFO_NULL, 0, |
| 22 | MPI_COMM_WORLD, |
| 23 | &intercomm, errcodes ); } |
| 24 | return n; |
| 25 | } |

Fig.5 MPI spawns new communicators.

#### B. *Fault Tolerant MPI Semantics and Interfaces*

 The MPI Forum's Fault Tolerance Working Group [6] has defined a set of semantics and interfaces to enable fault tolerant applications and libraries to be portably constructed on top of the MPI interface, which enables applications to continue running and using MPI if one or multiple processes in the MPI universe fail. We assume that MPI implementation provides the application with a view of the failure detector that is both accurate and complete. The application is notified of a process failure when it attempts to communicate either directly or indirectly with the failed process using the function's return code and error handler set on the associated communicator. The application must explicitly change the error handler to MPI_ ERRORS_RETURN on all communicators involved in fault handling on the application.

#### C. *MPI Recovery Procedure*

 To minimize the impact of the failure recovery process on an MPI/TCP task running on a cloud infrastructure, we propose a component that automates the launch and monitoring processes, periodically checks MPI health, and

stops and re-launches the MPI/TCP process if a failure is detected. Our component implements the following launch and monitoring steps and automated recovery flow process:

- 1. The MPI_INIT pings and establishes connections with each virtual machine, builds a communication group comprising all communicators, and ensures that the communicators are up and available.
- 2. The MPI process sends the size n node numbers, node names, folder path in which the MPI process will run, and file names with application instructions.
- 3. RPC initializes independent, long-term TCP connections.
- 4. Parallel execution enables each node to deploy multiple threads. A node is deemed to have failed if a virtual machine is in down status. MPI implementation must be able to return an error code if a communication failure such as an aborted process or failed network link occurs.
- 5. The management process uses MPI_Comm_Spawn to create workers and return an intercommunicator. This simplifies intercommunication formation in the scenario of parallel workers because one MPI_Comm_spawn command can create multiple workers in a single intercommunicator's remote group. MPI_Comm_spawn replaces dead workers, and continues processing with no fewer workers than before.
- 6. A parallel worker's processes can intercommunicate using an ordinary intercommunicator, enabling collective operations. Fault tolerance resides in the overall manager/worker structure.
- 7. The MPI process sends the size n node numbers, node names, folder path in which the MPI process will run, and file names with application instructions. RPC initializes independent, longterm TCP connections.
- 8. Checkpoints are copied from cloud storage.
- 9. Parallel execution enables each VM to deploy multiple threads. Note that our component is independent of any particular MPI application.

# D. *Fault Tolerance Implementations*

Focusing on communication-level fault tolerance issues, Figs 4 and 5 give an example of a common scenario based on a well-known master/worker communication program. The scenario covers program control management, failure detection, and termination detection. Fig 4 illustrates the general procedure for setting up a fault tolerance MPI/TCP working environment using inter-communicators and MPI_ERROR_Handlers. Fig 5 shows how MPI responds by spawning new nodes and removing dead nodes when a failure occurs. Fig 6 shows a diagram for the whole process.

![](_page_4_Figure_12.png)

Fig.5 MPI/TCP failure recovery process: (a) A set of virtual machines run in parallel (b) Node#2 fails (c) MPI locates a new node#3, which delivers the new node information to the upper layer (4) New TCP long connections are established.

#### *E. TCP Recovery*

 After the MPI connection is recovered, an RPC procedure is initialized. A client node calls its client stub using parameters pushed to the stack. The client stub packs these parameters into a message, and makes a system call to send the message from the client machine to the server machine. The operating system on the server machine passes the incoming packets to the server stub, and the server stub unpacks the parameters from the message. The server stub calls the server procedure, which forms the basis of establishing the TCP connection.

## F. *Higher Level Applications*

 An HPC–based cloud example is the design of a distributed master/worker finite element method (FEM) computing process. The FEM process involves mesh generation, refinement, and matrix assembly. The uncertainty of mesh refinement complicates the following operations: distributing basic functional modules that incorporate message synchronization, distributing matrices' data, and collecting data; however, a MapReduce HDFS can maintain the consistency of FEM meshes in a distributed environment. Assuming that the computing capability of each node in a cloud is identical, the process for solving this problem is to map all tasks to a set of cloud mesh data. An independent task assigned to a worker process has a well-defined life cycle: First the master sends a task to a worker, which the worker takes and works on; second, the worker returns the results after completing the task.

 The fault tolerant scheme collaborates with checkpoint/ restart techniques to handle failures during distributed processing. At least three lists task lists must be created: (1) Waiting (2) In progress (3) Done. The manager-part program should mark an intercommunicator as dead when a send or receive operation fails, maintain the task in-progress list, and send the operation to the next free worker. Global performance tuning optimization can be constructed from the timing and fault tolerant modes to identify the global minimum execution time for correct computing results.

## IV. CONCLUSION AND FUTUREWROK

The cloud has evolved into new computing clusters whereby resources deliver unique computational paradigm advantages for HPC and data-intensive computing. This in turn reduces costs for users in terms of purchasing and maintaining sophisticated hardware. We have investigated the advantages of using a cloud platform in the context of high-performance data-intensive computing, and analyzed the issues relating to the reliability of cloud environment. An MPI/TCP environment on a cloud is significant because it can support both asynchronous and synchronous distributed computing as well as various parallel programming models. We have proposed a failure recovery approach for handling errors in the MPI/TCP infrastructure and provided suggestions for data recovery in higher level applications.

 Our future work will involve formulizing the failure recovery approach with mathematical techniques that specify, verify, and validate the precision and accuracy of scientific

HPC and data-intensive algorithms on the cloud, and thus provide design assurance.

# References

- [1] Christian Vecchiola, Suraj Pandey, Rajkumar Buyya, "High-Performance Cloud Computing: A View of Scientific Applications", ISPAN '09 Proceedings of the 10th International Symposium on Pervasive Systems, Algorithms, and Networks, pp. 4-16, 2009.
- [2] Sanjay P. Ahuja, Sindhu Mani, "The State of High Performance Computing in the Cloud", Journal of Emerging Trends in Computing and Information Sciences, VOL. 3, NO. 2, February 2012 ISSN 2079- 8407.
- [3] R.J. Sobie, A. Agarwal, I. Gable, C. Leavett-Brown, M. Paterson, R. Taylor, "HTC Scientific Computing in a Distributed Cloud Environment", Proceedings of the 4th ACM workshop on Scientific cloud computing , pp. 45-52, ACM New York, NY, USA ©2013 ISBN: 978-1-4503-1979-9 doi>10.1145/2465848.2465850.
- [4] Abhishek Gupta, Dejan Milojicic, "Evaluation of HPC Applications on Cloud", HP Laboratories, HPL-2011-132, August 21, 2011.
- [5] Naidila Sadashiv, S.M. Dilip Kumar, "Cluster, grid and cloud computing: a detailed comparison", The 6th international conference on Computer science and education, Singapore, Aug 3-5,2011.
- [6] Jeffrey Dean and Sanjay Ghemawat, "MapReduce: Simplified Data Processing on Large Clusters", OSDI'04: Sixth Symposium on Operating System Design and Implementation, San Francisco, CA, December, 2004.
- [7] Grzegorz Malewicz, Matthew H. Austern, Aart J.C Bik, James C. Dehnert, Ilan Horn, Naty Leiser, Grzegorz Czajkowski, "Pregel: a system for large-scale graph processing" Proceedings of the 2010 ACM SIGMOD International Conference on Management of data, pp. 135-146, ACM New York, NY, USA, 2010
- [8] K. Shvachko, Hairong Kuang, S. Radia, R. Chansler, "The Hadoop Distributed File System", 26th IEEE Symposium on Mass Storage Systems and Technologies (MSST), Incline Village, NV, 2010.
- [9] Ralf Lämmel: "Google's MapReduce programming model Revisited", Sci. Comput. Program. 70(1): 1-30 (2008).
- [10] Yucheng Low, Danny Bickson, Joseph Gonzalez, Carlos Guestrin, Aapo Kyrola, Joseph M. Hellerstein, "Distributed GraphLab: a framework for machine learning and data mining in the cloud", Proceedings of the VLDB Endowment VLDB Endowment Hompage archive, Volume 5 Issue 8, pp.716-727, April 2012.
- [11] Alain Tchana, Laurent Broto, Daniel Hagimont, "Fault Tolerant Approaches in Cloud Computing Infrastructures", ICAS 2012 : The Eighth International Conference on Autonomic and Autonomous Systems, St. Maarten, Netherlands Antilles, Mar25-30,2012.
- [12] http://meetings.mpi-forum.org/mpi3.0_ft.php
- [13] Fault Tolerance Working Group, "Run-though stabilization inter-faces and semantics," svn.mpi-forum.org/trac/mpi-forumweb/wiki/ft/ run through stabilization.
- [14] L. Lamport, R. Shostak, and M. Pease, "The byzantine generals problem," ACM Transactions on Programming Languages and Systems,vol. 4, no. 3, pp. 382–401, 1982.

