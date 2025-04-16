# Leveraging Code Snippets to Detect Variations in the Performance of HPC Systems

Jidong Zhai , Liyan Zheng , Jinghan Sun, Feng Zhang , Xiongchao Tang, Xuehai Qian, Bingsheng He, Wei Xue, Wenguang Chen, and Weimin Zheng

Abstract—Variations in the performance of parallel and distributed systems are becoming increasingly challenging. The runtimes of different executions can vary greatly even with a fixed number of computing nodes. Many HPC applications on supercomputers exhibit such variance. This not only leads to unpredictable execution times, but also renders the system's behavior unintuitive. The efficient online detection of variations in performance is an open problem in HPC research. To solve it, we propose an approach, called VSENSOR, to detect variations in the performance of systems. The key finding of this study is that the source code of programs can better represent performance at runtime than an external detector. Specifically, many HPC applications contain code snippets that are fixed workload patterns of execution, e.g., the workload of an invariant quantity and a linearly growing workload. This observation allows us to automatically identify these snippets of workload-related code and use them to detect variations in performance. We evaluate VSENSOR on the Tianhe-2A system with a large number of parallel applications, and the results indicate that it can efficiently identify variations in system performance. The average overhead of 4,096 processes is less than 6% for fixed-workload v-sensors. We identify a problematic node with slow memory by using VSENSOR that degrades the performance of the program by 21%. A serious issue with network performance is also detected that slows down the Tianhe-2A system by 3.37 times for an HPC kernel.

Ç

Index Terms—Parallel computing, performance variance, HPC, performance analysis, performance optimization

# 1 INTRODUCTION

CURRENT large-scale, high-performance computing (HPC) systems [1], [2], [3] suffer from serious variations in performance. Because of this [4], the runtimes of different executions of the same application may vary considerably. This behavior is very common in major HPC centers, and an example is shown in Fig. 1. On a fixed number of nodes of the Tianhe-2A supercomputer [5], the NPB-FT program in CLASS D using 1,024 processes was executed many times. A segment of a longer execution is shown in Fig. 1. The

Recommended for acceptance by D. Li.

Digital Object Identifier no. 10.1109/TPDS.2022.3158742

system itself or other jobs generated background noise. The variance in performance across different executions was significant, and the longest runtime was more than three times the shortest one.

Both normal users and application developers can be adversely affected by the prevalent variance in performance. For common users, it can lead to unexpected behavior by an executing application, leading to violations of performancerelated requirements and higher resource costs. Furthermore, it becomes complicated to measure and compare the performance of different programs. For application developers, the background variance in performance can hide the advantage of a novel optimization technique. Based on previous work [3], [6], [7], the variance in performance can be caused by a number of reasons, e.g., network contention, OS schedule, zombie processes, and hardware faults. Certain types of variances in performance can be successfully prevented according to their causes, whereas others are not preventable. For instance, if a problematic node leads to a variance in performance, system users can replace it with another node and execute the job again. By contrast, users have few options for avoiding the variance caused by network contention because the network is generally shared by many users. Therefore, we need to understand two key issues before we re-submit a job or blame the system for such variation: 1) the degree of the variance in performance, and 2) its root cause.

Four main methods are currently used to identify variance in the performance of applications, but none of these is good enough to address the two challenges stated above. 1) Rerun. A basic way of observing variance in performance is to execute a program many times and calculate the durations of different executions. This strategy consumes more

Jidong Zhai, Liyan Zheng, Xiongchao Tang, Wei Xue, Wenguang Chen, and Weimin Zheng are with the Department of Computer Science and Technology, Tsinghua University, Beijing 100084, China. E-mail: {zhaijidong, xuewei, cwg, zwm-dcs}@tsinghua.edu.cn, zhengly20@mails.tsinghua.edu. cn, tomxice@gmail.com.

Jinghan Sun is with the Department of Computer Science, University of Illinois Urbana-Champaign, Champaign, IL 61820 USA. E-mail: js39@illinois.edu.

Feng Zhang is with the Key Laboratory of Data Engineering and Knowledge Engineering (MOE), School of Information, Renmin University of China, Beijing 100872, China. E-mail: fengzhang@ruc.edu.cn.

Xuehai Qian is with the Ming Hsieh Department of Electrical Engineering, University of Southern California, Los Angeles, CA 90007 USA. E-mail: xuehai.qian@usc.edu.

Bingsheng He is with the School of Computing, National University of Singapore, Singapore 119077. E-mail: hebs@comp.nus.edu.sg.

Manuscript received 14 Nov. 2021; revised 4 Feb. 2022; accepted 8 Mar. 2022. Date of publication 15 Mar. 2022; date of current version 11 July 2022.

This work was supported in part by the National Key R&D Program of China under Grant 2017YFA0604500, in part by the National Natural Science Foundation of China under Grant U20A20226, in part by Beijing Natural Science Foundation under Grants 4202031 and L192027, and in part by Tsinghua University-Peking Union Medical College Hospital Initiative Scientific Research Program under Grant 20191080594. (Corresponding author: Jidong Zhai.)

<sup>1045-9219 © 2022</sup> IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

![](_page_1_Figure_1.png)

Fig. 1. Variation in performance with a fixed number of computing nodes. The runtime of NPB-FT using 1,024 processes varied significantly among different executions on a fixed number of nodes of the Tianhe-2 HPC system.

resources of the system and requires a long time for re-executions. 2) Performance models [1], [8]. An accurate performance model estimates the execution time of an application to measure the difference between its estimated and observed performance. However, most models can estimate only the total variance in performance, rather than identifying the cause of such variance. In addition, the performance model is usually not portable. The model designed for one program usually fails to deliver satisfactory predictions for another program. 3) Tracing and profiling [9], [10]. These methods have major drawbacks even though they have been used in many cases. Due to the omission of information on the time sequence of applications, profiling-based methods fail to find time-dimensional variance in performance. Tracing-based methods generate massive amounts of trace data, particularly with the increase in the size of the problem and scale of the job [11]. Moreover, the overhead of tracing-based methods limits their use for identifying variance in performance on the fly. Even with trace compression techniques [12], [13], [14], knowledge of the application is necessary to understand the collected traces, which is not practical for normal users. 4) Benchmarking. With benchmarks of fixed-work quanta (FWQ), we can measure the variance in performance. When a fixed amount of work is executed repeatedly, we can observe a variance in performance if the execution times vary for the same job. For instance, the variance in network performance may be identified continuously by conducting and detecting the same communication. The key problem is the intrusiveness of this approach: It may incur extra variance in performance due to the contention for resources between the benchmarks and the original application. It is therefore not suitable for production programs.

Although a considerable amount of research has been dedicated to detecting the variance in performance and its root causes, successful detection on the fly remains an outstanding problem for large-scale parallel applications.

To solve this problem, we develop VSENSOR, which is a light-weight approach for detecting variance in HPC applications on the fly. VSENSOR focuses on performance variance caused by external environment, including resource contention, hardware problems, and other environment effects. VSENSOR detects long-lasting performance which can greatly affect the execution of applications. Our main insight is that common parallel applications may include code snippets that exhibit the same FWQ benchmark behavior. Many code fragments in a loop, for instance, may execute in a similar manner in multiple iterations. Such snippets can be regarded as FWQ benchmarks incorporated into a program. We call such a snippet a v-sensor. V-sensors can detect variance in performance during execution without significant overhead. Using v-sensors to track variance in the performance of applications has three advantages: 1) There is no need for a performance model, which can be very difficult to implement. 2) It has low interference and the minimum cost. During execution, VSENSOR does not need to run external programs, such as external benchmarks. This prevents overhead and resource contention owing to monitoring daemons. 3) V-sensors can make the identification of the root causes of a variance in performance easier.

However, we need to handle two challenges in implementing v-sensors as a tool to detect variance in performance. 1) Detection of v-sensors. It is challenging to identify v-sensors in a large amount of code; for instance, various workloads can be processed by snippets in different iterations, various arguments can influence program behavior, and programs can take various paths. For complicated applications, it is unrealistic for programmers to mark vsensors by themselves, even if they are well understood for the given application. 2) Reducing on-the-fly tracking overhead. Although v-sensors belong to the original applications, the variance in performance still needs to be observed by additional analysis and measurement. We need to reduce the overhead to prevent increasing the execution time or exacerbating the variance.

To handle these difficulties, we use a hybrid staticdynamic method for program analysis. During compilation, we provide a propagation algorithm with dependence to automatically locate the v-sensors, and then create and set suitable v-sensors. During runtime, we develop a light-weight analytical algorithm to identify the variance in performance on the basis of the v-sensors on the fly. We use the characteristics of the v-sensors to identify the variance in their performance by comparing them with historical data on their behavior. By comparing the performance of the v-sensors in different processes on a large-scale parallel system, we identify the variance in performance among processes.

We develop VSENSOR as a tool chain integrated with the LLVM [15] to measure the efficacy of our method. VSENSOR requires the source code of applications, and applications should have repeated executed snippets, which are usually common for HPC programs. It supports HPC applications written in MPI [16]. In experiments, VSENSOR was tested on 4,096-process MPI programs on the Tianhe-2A HPC system. Results show that VSENSOR can detect v-sensors, and incurs an overhead of only less than 6% by using fixed-workload vsensors for the online detection of variance. Two more classes of v-sensors, i.e., regular-workload v-sensors and external v-sensors, significantly enhanced the capability of detection and applicability of our tool. We also verify the usefulness of VSENSOR in empirical scenarios: In the Tianhe-2A system, it detected a bad node that degraded the performance of the CG by 21%. A serious issue in the network, which had caused the FT program to slow down by 3.37, was also identified by VSENSOR.

We make the following contributions in this paper.

- We obtain the key insight that fixed-work quanta benchmarks inside applications, called v-sensors, are valuable for detecting variance. We also propose a light-weight online performance variance detection algorithm based on the v-sensors.
- We develop VSENSOR, a tool to detect variance in performance, for HPC applications that can automatically identify v-sensors in the source code by using a combination of static and dynamic analyses.
- We evaluate VSENSOR on up to 4,096 processes, and verify its ability to identify an issue in the network that slowed the application down by 3.37.

The remainder of this paper is arranged as follows. A general design of the system of v-sensor is provided in Section 2. The v-sensor search method during compilation is given in Section 3. V-sensors with variable workload, i.e., regular v-sensors, are detailed in Section 4. Rules for the selection of v-sensors are described in Section 5. The on-thefly detection algorithm is provided in Section 6, and the results of evaluation are given in Section 7. Section 9 provides a summary of related work in the area, and we give the conclusions of this study in Section 10.

# 2 VSENSOR DESIGN

The key idea of VSENSOR is to locate code snippets with certain recognizable patterns, i.e., v-sensors, in user programs to detect system-wide variance in performance via their runtime statistics. We classify v-sensors inside user programs into two categories: fixed v-sensors and regular v-sensors. Fixed-workload v-sensors execute a constant sequence of instructions for each occurrence. Due to their property of a fixed workload, the variance in their execution times can directly reflect the variance in the performance of the system on which they are running. Code snippets with variant sequences of instruction execution are still eligible as variation sensors: for instance, if they always execute a multiple of the same set of workloads. Such a scenario occurs in applications—a loop structure executed with different numbers of iterations under different program states. We define all such eligible variant sensors as regular v-sensors. We normalize the execution time series of regular v-sensors to detect system variance. A formal and generalized definition of regular v-sensors is given in Section 4, and its normalization is discussed in Section 6.2.

Fixed sensors and regular sensors constitute internal v-sensors, and rely on user programs. On the contrary, external vsensors use external benchmarks to detect variance in performance; this is an auxiliary method for programs with an insufficient number of internal v-sensors. We discuss the use case and trade-off between extra sensing coverage (i.e., the ratio of execution time covered by v-sensors to the whole execution) and overhead for external v-sensors in Section 5.2.

With the help of these kinds of v-sensors in an application, the variance in performance of programs can be evaluated during execution. We develop VSENSOR as a performance tool for large-scale HPC applications.

VSENSOR is composed of a dynamic module and a static module. The static module automatically detects v-sensors

![](_page_2_Figure_12.png)

Fig. 2. VSENSOR workflow.

with the help of compiler technologies. We use LLVM [15] to locate v-sensors in our system. To process applications written in different languages, such as FORTRAN, C, and C++, we develop this implementation by analyzing the LLVM intermediate representation (LLVM-IR). However, most HPC applications are not compiled by LLVM but by vendor compilers to optimize their performance. Therefore, to allow developers to use their preferred compiler, VSENSOR performs a source-to-source instrumentation. Developers instrument the source code of applications by VSENSOR and compile the instrumented code with their preferred compiler.

The dynamic module gathers data on the fly, performs performance analysis at runtime, and provides a performance summary. The summary is updated during application execution, and allows users to check the real-time results before the program finishes execution.

We show the workflow of VSENSOR in Fig. 2. The steps shown in the figure are described next.

1 Compile. VSENSOR uses the LLVM to map the original source code to the LLVM-IR.

2 Identify v-sensors. The LLVM-IR provides instructions and basic blocks for a given program. The v-sensor detection algorithm provided in Section 3 and Section 4 is executed at this level. Our tool then handles the call graph of the program to process special situations, such as recursive calls. VSENSOR then analyzes the loops and function calls. It also analyzes the behavior of the v-sensor in multiple processes in parallel programs because it targets multi-process applications.

3 Map to source. The LLVM-IR provides the v-sensors that are detected in step 2, and our tool can locate them in the source code.

4 Instrument. In this step, our tool carries out instrumentation in the source code based on information obtained in the previous step. To obtain a reasonable v-sensors selection during instrumentation, we use multiple rules for guidance that are detailed in Section 5.

5 Compile. To maintain the special optimizations in the compilers, we use the default compilers and the original compiling arguments to compile the instrumented code and the revised programs.

![](_page_3_Figure_1.png)

Fig. 3. V-sensor.

6 Run. In this step, our tool executes the updated program in real environments. During runtime, it generates the related performance monitoring data by using customized functions with instrumentation.

7 Analyze. Note that the performance data are subjected to a preprocessing step so that they can be used to detect variance. By comparing the gathered data with historical records, our algorithm detects variance in each process during runtime as detailed in Section 6. The data gathered from the same v-sensors in different processes are used to identify variance in performance among processes.

8 Visualize. Finally, our tool generates figures to show the distribution of the variance in performance. Note that the results are updated on the fly because new contents are continuously generated and analyzed during an execution.

In summary, there are three steps to apply VSENSOR for users. (1) Running the static module of VSENSOR with the source code of the application. VSENSOR automatically identifies and instruments v-sensors in the application. This is a source-to-source transformation. (2) Compiling the instrumented application code. Users compile the instrumented application containing v-sensors with any preferred compiler. (3) Running applications. VSENSOR starts detection when the application is executed. The reports of VSENSOR are automatically generated.

In the following sections, we first introduce the v-sensor identification in Step 2, which is introduced in Sections 3 and 4. The source code modification in Step 4 is elaborated in Section 5. The data analysis in Step 7 is explained in Section 6.

# 3 FIXED WORKLOAD V-SENSORS

In this section, we define the v-sensor and develop a dependence propagation algorithm to identify it. We show our basic ideas in C language and illustrate our examples in MPI [16], which is popular in HPC. Note that we use the LLVM-IR to show our algorithm, but our approach also works on other parallel applications based on message passing.

#### 3.1 Fixed Workload V-Sensor Definition

In the v-sensor design, we use v-sensors as benchmarks integrated within HPC applications. we regard a code snippet in a loop as a v-sensor, therefore, the v-sensor runs repeatedly. Note that the number of snippets within the loop can be large. Accordingly, we define a fixed v-sensor in a loop as a code snippet with fixed amount of work in it. We show this in Fig. 3, in which we regard snippet-2 as a v-sensor with a fixed workload in the for loop.

To maintain an appropriate overhead for online detection and instrumentation, we need to carefully select the granularity of the v-sensor, although the code snippet can Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

![](_page_3_Figure_13.png)

Fig. 4. Code examples for VSENSOR.

be very small according to the definition. In our design, we consider only function calls and loops as candidates for vsensors.

The idea underlying VSENSOR is shown in Fig. 4, where we assign identifying numbers to function calls and loops. We highlight the arguments in the functions, variables in the loops, and global variables. Note that in this case, v-sensor candidates for Loop-2 are Call-1 and Call-2, and the Loop-4 v-sensor candidate is Loop-5. However, the count++ statement is not a v-sensor candidate for Loop-3 because the statement is not a function call or a loop.

We now establish the concept of the quantity of work. Our code snippets are categorized according to their purposes into three types: IO, network, and computation snippets. In Fig. 4, Call-3 is a network snippet and Loop-4 is a computation snippet. The fixed workload standard for each type of snippet is different. The criterion for calculating the quantity of work is always based on user-defined standards, even for the same kind of fragments. Our default decision rules are shown as follows, and our tool allows users to add constraints:

- Computation. Computation v-sensor means that among different iterations, the computation snippet is related to the same instruction sequence.
- Network. Network v-sensor means that for a communication operation, the message size, source, and destination processes (or communicators) remain unchanged among different iterations.
- IO. IO v-sensor means that for a given IO operation, the sizes of the data and target devices do not change.

VSENSOR permits users to identify certain factors determining v-sensors to guarantee versatility, which is controlled by a configuration file. For instance, the same sequences of instructions with various cache miss rates can result in different behavior, and users can determine whether a constant rate of cache error should be an additional requirement for v-sensors. More variables, including IO frequency and network distance, can be used as dynamic rules on runtime information, or as static rules that are only available at compilation time.

The effect of additional rules on the choice of v-sensors is shown in Fig. 5. Static rules for v-sensor selection are used during compilation. More severe static rules intuitively generate fewer v-sensors. v-sensors can be further classified based on online information by using the dynamic rules. As is shown in Fig. 5, our tool identifies v-sensors based on static rules and ignores all dynamic rules during compilation. Note

![](_page_4_Figure_1.png)

Fig. 5. Static rules and dynamic rules.

that the v-sensors are also classified into two groups during runtime based on their performance-related data that are available only during execution. The variance in the performance of each group can be identified using dynamic rules.

In MPI communication, network destinations should be used in static rules for applications as they are normally available during compilation. Conversely, the rate of cache misses can be considered only as a dynamic rule. With regard to the range of rates of cache misses, such as 0% to 10%, or 10% to 20%, we can classify performance records during runtime into different groups.

A more severe rule results in fewer v-sensors, so the sensing coverage decreases as well. Since VSENSOR is mainly used to detect large performance variance, too strict rules are not necessary. Even though a little variation of workload exists, it can be covered by a more significant performance variance.

#### 3.2 Analysis of Intra-Procedure

This section provides the intra-procedural analysis of code snippets that invoke no function. The candidate v-sensors considered in this analysis are pure loops with computations because in most cases, programs call functions for IO and network operations. The workload of the snippet is fixed if its instruction sequence is not modified during iterations, under the rules mentioned in Section 3.1. Therefore, the quantity of work is determined by the branch statements and loops. A candidate is not a v-sensor if it contains a control expression that is influenced by variables between executions. In our design, we execute a compiler technique, called use-define chain analysis, to analyze the dependence between variables.

Pure computation snippets are shown in Fig. 6. There are three subloops of the outermost loop (Loop-n), Loops-1, -2, and -3. Both Loop-1 and Loop-2 use the index of Loop-n, which is n. Loop-1 and Loop-2 are not v-sensors of Loop-n

![](_page_4_Figure_9.png)

Fig. 6. Example of intra-procedural analysis.

![](_page_4_Figure_11.png)

Fig. 7. Illustration for the principle of the analysis of inter procedure.

because the variable n is updated between their executions. By contrast, the variable n does not influence Loop-3's control expression, and thus its quantity of work is unchanged during iterations of Loop-n. Based on this analysis, Loop-3 is a v-sensor of Loop-n.

Fig. 4 shows that Loops-3 and -5 are the v-sensors of Loops-1 and -4, respectively, according to our intra-procedural analysis.

#### 3.3 Analysis of Inter-Procedure

The principles of our inter-procedural analysis are illustrated in Fig. 7. Assume that three calls C1, C2, and C3 are made to the function F within loop L, and a snippet S exists in F. If the following conditions are met, S qualifies as a vsensor of L:

- For all parent loops within F, snippet S is a v-sensor. This implies that the quantity of work of S is invariant during the execution of F.
- For all invocations of F within L, which are C1, C2, and C3, if the global variables or partial arguments of F influence S's quantity of work, they must be invariant during iterations of L. Hence, among the invocations of F, S's quantities of work are the same.

We provide an example of the dependency propagation of inter-procedural analysis in Fig. 8. It shows how to decide whether a function call belongs to a v-sensor. Fig. 8 shows the dependency relation obtained from the inter-procedural analysis, and the argument–workload relations for each function need to be analyzed. For instance, the GLBV global variable and the x argument influence the workloads of foo. If GLBV and x remain invariant among calls, foo processes the same amount of work. As k does not influence the control sequence of the foo function, Call-1 is a v-sensor of Loop-2. By contrast, Call-1 does not act as a v-sensor for Loop-1 because n is updated during its iterations. Furthermore, Call-2 is not a v-sensor of Loops-1 and -2.

In Fig. 8, we take Loop-5, a v-sensor of Loop-4, as an example for illustration. Loop-5 also acts as a v-sensor for both Loop-1 and Loop-2 because it depends on neither global variables nor function arguments. Because the x argument is updated during different invocations of Call-2, Loop-4 does not act as a v-sensor of Loop-2.

#### 3.4 Multiple Process Analysis

The workload for each process needs to be analyzed for multi-process programs, such as MPI programs. In Fig. 9, we show an instance of a snippet for which the workload remains the same during the iterations but changes among processes. Each process obtains a rank ID from MPI_- Comm_rank. The rank influences the workload of Loop-1. For various processes, the workloads are different, but for

![](_page_5_Figure_1.png)

Fig. 8. Example of inter-procedural analysis.

![](_page_5_Figure_3.png)

Fig. 9. Analyzing different processes.

the same rank, its workload remains the same among different iterations. Specifically, only the odd-ranking processes need to execute count++. To detect inter-process variance at runtime, VSENSOR uses snippets that have fixed workloads for all processes.

To analyze the dependence between process ranks and workloads, we apply a similar method. First, we need to identify the functions, such as MPI_Comm_rank, gethostname, that can specify the process IDs. Second, the relation between the quantity of work and process ID (such as host names and rank IDs) needs to be examined. Third, the snippet is regarded as having a fixed workload among processes if it is not influenced by rank variables.

#### 3.5 Whole Program Analysis

In this section, we show the method to analyze different procedures. To determine the order of analysis, we perform a topological sort of the call graph of a given program. A bottom-up analysis of the program is conducted on the call graph of the application. To transmit the information of the entity called to the caller, we need to analyze the former before its related caller. In this way, we can detect v-sensors for inter-procedural analysis.

We need to deal with some special situations. Cycles are created by recursive calls among the call graphs of an application, where this can deter the sorting of the topology. For applications with function pointers, it is difficult to detect call targets during compilation. Thus, we remove invocations to function pointers in the call graph of a program. Fig. 10 illustrates this procedure. Although removing function pointers can decrease detection coverage of execution, v-sensors within invoked functions are still available.

Many applications may call external functions whose codes cannot be accessed, such as the MPI functions fopen, and printf. We cannot analyze program behavior during compilation without the code. Hence, we use a traditional method: We regard an external function that does not have any descriptions as having a never-fixed workload, which

![](_page_5_Figure_11.png)

Fig. 11. Instruction sequence.

indicates that snippets with invocations to functions with the never-fixed workload are not regarded as v-sensors. This method can prevent false positives, although some real vsensors may be missed as well. Moreover, we provide the flexibility whereby users can determine the behaviors of external functions, such as arguments that may influence the workload, by themselves, and our tool offers descriptions of the prevalent functions in the C and MPI libraries.

# 4 REGULAR WORKLOAD V-SENSORS

In this section, we formally define regular-workload v-sensors, provide concrete examples, and discuss how to identify them via compiler techniques.

#### 4.1 Instruction Sequences

Code snippets with a fixed runtime workload can be used as variant sensors because they execute the same instruction sequence each time. Two identical instruction sequences are comparable in terms of their execution times, and the difference between them directly reflects system-wide variance in performance. To reflect variance, however, the instruction sequences need not be exactly the same. In Fig. 11, we use different colors to denote different instructions. Each pair of instruction sequences 1 and 2 in this figure is a multiple of the same sequence of instructions, and we define such a pair of instruction sequences as comparable. The execution times of comparable sequences can reflect system variance once they have been normalized with a factor of their multiplicity of the instruction set common to them.

#### 4.2 Regular Workload Definition

The key insight of the previous section is that any two comparable instruction sequences can be used to detect variance. As a result, we can leverage code snippets with varying workloads as variant sensors as long as any pair of comparable instruction sequences occurs in their executions. We define such code snippets as regular-workload vsensors. We use different colors to denote different sets of comparable sequences in Fig. 12. In the fixed-workload Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

Fig. 12. Fixed and regular workload comparison.

sensor, all execution sequences are identical and thus comparable to one another. The regular-workload sensor shown in the figure contains two separate sets of comparable instruction sequences. Although the three instruction sequences in blue have different multiplicities (3, 2, 1), they have a common instruction set, and can thus be used to detect variance in performance.

We provide a concrete example of such regular-workload v-sensors. Fig. 13 shows two nested loops, L1 and L2. The inner loop L2 has a varying workload depending on the iterating variable of the outer loop. With the increase in the value of n, the inner loop increases its range of iteration and enters different branch statements, and then executes a constant function call. In its first two occurrences, it executes function call fooðÞ once and twice, respectively. The sequences of instruction execution of these two occurrences are comparable as they are multiples of the same instruction sequence of function fooðÞ. A similar analysis is applied to its third and fourth occurrences, which execute function barðÞ different numbers of times. Therefore, loop L2 is a regular-workload v-sensor as it contains two different sets of comparable instruction sequences.

## 5 PROGRAM INSTRUMENTATION

#### 5.1 V-Sensor Selection

Having discussed different types of v-sensors in Section 3, we now show in this section how to choose appropriate vsensors for instrumentation. We use the instance in Fig. 14 for illustration.

- Scope. The scope of a snippet implies the loop within which it is a valid v-sensor. Fig. 14 contains two vsensors, S1 and S2, and two loops, L1 and L2. The scope of S2 is L1, which is larger than L2 for S1. S1's workload varies among the iterations of L1 but remains invariant among those of L2. In the iterations of L1, S1 cannot use data from its previous

| L1 for (n=0; n<4; ++n) { | n | L2 | for (k=0; k <=n; ++k) { |  |
| --- | --- | --- | --- |
| 0 | S1 if(n <= 1){ | 1 | foo(); // constant |
| 2 | s2 | else{ | 3 |  |
| bar(); // constant |  |  |  |

![](_page_6_Picture_10.png)

Fig. 13. Illustration of a code snippet for v-sensor with a regular workload.

![](_page_6_Figure_12.png)

Fig. 14. V-sensor scope.

iterations because they could have been updated. Therefore, a v-sensor that has a wide range gathers more durable data that can be applied to identify variance in performance during a longer period. The snippets have a global scope or whole-program scope if they belong to v-sensors in the outermost loop, and are called global v-sensors. In our design, we select global v-sensors for instrumentation.

- Granularity. A compromise between the capacity for detection and the consequent overhead must be considered. Although snippets of small sizes can detect the variance in performance in a fine-grained manner, they are costly in terms of performance. By contrast, large snippets can ignore the variance in performance at a high frequency. In our design, users can set the value of max-depth: depth-0 is the outermost loop, and our tool instruments v-sensors that are at depths of less than max-depth.
Nevertheless, we can obtain only the execution time of a v-sensor during runtime, and the analysis during compilation is a mere prediction. Hence, optimizations during runtime are used to minimize the cost incurred by fine-grained methods, and are detailed in Section 6.

- Nested v-sensors. In the presence of nested v-sensors, at most one of them is instrumented because the auxiliary functions instrumented by VSENSOR have varying workloads. If the v-sensors are instrumented inside, the outside v-sensor contain a function for instrumentation and hence are disqualified from consideration as v-sensors. We instrument the outermost v-sensors in our design.
To assess the performance of the v-sensor from a temporal perspective, our tool instruments special functions, such as Tick and Tock shown in Fig. 3, before and after their execution during compilation. Then, these functions trigger the algorithm to detect variance in performance.

### 5.2 Inserting External V-Sensors

Leveraging code snippets in user programs as sensors of performance variance introduces a slight overhead to the original application, but such v-sensors are uncontrollable in terms of their distribution and duration at runtime. How-

ever, it is expected that VSENSOR has a more evenly Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

![](_page_7_Figure_1.png)

Fig. 15. Illustration for inserted fixed-work.

distributed sensing period during program execution to minimize potentially undetected problems of system variance in these uncovered periods. To achieve this goal, VSEN-SOR provides (1) a code instrumentation mechanism at compilation that inserts function calls of predefined benchmarks into the original programs, and (2) a trigger mechanism that uses a user-defined policy and triggers the vsensors selectively. For the sake of clarity, we define such inserted sensors as external v-sensors and those identified in the original programs as internal v-sensors.

Fig. 15 shows an example of an external v-sensor. The function calls are inserted at the beginning of the body of the loop, within which a pre-defined fixed-workload benchmark is executed after checking the trigger condition. If they are triggered, we treat such inserted sensors as identical to fixedworkload v-sensors when computing the overall system variance. In VSENSOR, we use FWQ/FTQ [7] as the default workload for external v-sensors. We also expose the interfaces to users so that they can define their own workload.

The triggering mechanism of external v-sensors in our tool enhances users' control of the coverage time of the sensors, and their distribution and overhead. Users can provide their own policy to VSENSOR that defines a trigger condition for each external v-sensor. In the current implementation, users are allowed to define the following control parameters:

- Minimum interval: The minimum interval between triggered v-sensors. Both internal and external v-sensors are taken into account.
- Duration: The duration of each external v-sensor.
- Maximum overhead: The maximum performance overhead introduced by external v-sensors. The performance overhead of external v-sensors is monitored at runtime. If it is excessive, the subsequent external v-sensors are disabled until the overall overhead falls below a given threshold.

## 5.3 Analyzing External V-Sensors

We show such a mechanism in Fig. 16. The first two external sensors cannot be triggered because they are too close to the previous v-sensor. The third one satisfies the minimum interval requirement, and is allowed to execute for a predefined duration. It is also possible for an external v-sensor not to be triggered if the maximum tolerable overhead is reached.

![](_page_7_Figure_11.png)

![](_page_7_Figure_12.png)

Fig. 17. Relation between ideal overhead and extra coverage provided by external v-sensors.

The external v-sensors can control sensing distribution much better than internal v-sensors, and help increase sensing coverage but introduce additional overhead to the program. To quantify this overhead, we build a performance model and discuss the trade-off between the increase in coverage and the additional overhead.

Suppose that the sensing coverage without external vsensors is C0 with performance overhead H0. Overhead H0 is relatively low because the internal v-sensors leverage code snippets in the original program as variance benchmarks, and introduce only such additional work as timestamp retrieval and variance analysis. External v-sensors, however, insert and trigger external benchmarks that increase coverage while imposing a larger overhead. Assume that the additional coverage is DC, and the overall overhead of both internal and external v-sensors is H. The relationship between DC and H is

$$H\geq H_{0}+{\frac{\Delta C}{1-C_{0}-\Delta C}}$$

The formula indicates a higher overhead as the original sensing coverage C0 increases, which is also shown in Fig. 17. We show how the ideal overhead of VSENSOR grows to achieve the designated additional coverage under different initial coverages. With a 20% overhead being introduced, 16.7% additional coverage is obtained when there is no internal v-sensor. If the initial coverage is 50%, we can achieve additional coverage of only 8.3% with the same overhead. In summary, external v-sensors are more efficient when the sensing coverage of internal v-sensors is low. Thus, external v-sensors are expected to play a key role in detecting variance in performance if fixed-workload code snippets are rare in the original program. The choice of different kinds of v-sensors is decided by VSENSOR. Compared with external v-sensors, both fixed-workload v-sensors and regular workload v-sensors are preferred because of their negligible overhead. If the sensing coverage of them is less than a user-defined threshold, external v-sensors are enabled to detect variance.

# 6 RUNTIME PERFORMANCE VARIANCE DETECTION

We show in this section how to use the gathered perfor-

mance data to detect variance in performance. Fig. 16. External v-sensors. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

![](_page_8_Figure_1.png)

Fig. 18. Background noise filtering.

#### 6.1 Smoothing Data

Due to interruptions in operating systems, HPC systems usually contain noise that is short but has a high frequency. Because the noise is usually generated in the kernel [7], it typically cannot be avoided, and has a regular periodical pattern. We regard system noise as a system characteristic instead of an instance of variance in performance. VSENSOR focuses on periodic and long-lasting variance in performance, but some v-sensors with short durations can be influenced by noise, and can yield false alerts. To avoid false-positive results, we aggregate and average performance data during a small time slice (1000us by default) to smooth data. The length of small time slices is customizable for users, as different systems have various characteristics depending on their OS and hardware.

We illustrate noise under time resolutions of 10 us and 1000 us in Fig. 18, where the v-sensors have a periodic workload that takes about 10 us to execute. For each execution, its wall time is recorded. The performance data appear to be unstable at a high resolution (10 us), but when we calculate with the longer period of 1000 us, its plot becomes smooth. Using this method, we can focus on significant and long-lasting variance in performance because a large amount of noise is filtered out. Moreover, the overhead owing to fine-grained v-sensor is reduced because our analysis algorithm is executed only once in a time slice.

Smoothing only filters out regular high-frequency variance and does not hinder the other variance detection. In the following calculation of application performance,

$$Perf=\frac{\Sigma_{i=0}^{n-1}cnt_{i}\times Time_{i}}{\sum_{i=0}^{n-1}cnt_{i}\times\min_{i=0}^{n-1}Time_{i}}\tag{1}$$

where Timei is the average execution time of v-sensors in a time slice and cnti is the count of executions. When there is a variance, the numerator in Equation (1) is not influenced by the smoothing, since it is always equal to the total execution time of v-sensors. However, the denominator can be different with or without smoothing. If a high-frequency variance happens on all processes and all the time, such as OS noises, Timei increases after smoothing as well as minn1 i¼0 Timei in the denominator. But for other types of variance that are non-periodical or have low frequency, not all time slices are influenced by it. Hence, the minimum of time slices, i.e., minn1 i¼0 Timei, does not change. Therefore, only regular high-frequency variances are filtered out. Long-lasting performance variance, focused by VSENSOR, will not be missed after smoothing.

#### 6.2 Normalizing Performance

We claim that v-sensors can be categorized into those for IO, network, and computation in Section 3.1. The v-sensor method allows us to find reasons for the observed variance in performance. In addition, multiple v-sensors of the same kind reflect the same aspect of the system, and hence these performance data can be combined to boost the precision of detection. For instance, assuming that we have 10 network vsensors that are invoked once every 1000 us, we can analyze at a granularity of 1000 us for each v-sensor. We can then perform a joint analysis with all v-sensors together at a finergrained granularity, such as 100 us, that can help us better grasp the variance in network performance. Because various v-sensors do not relate to the same workloads, we can use only the normalized performance instead of comparing direct execution times: We normalize the record with the fastest speed to 1.0 and compare each record to it. For example, the normalized performance of a record that takes twice as long as the fastest one is 0.5. The same kind of v-sensors indicate a certain part of the HPC system, and thus their normalized performance indicates the performance of the part they represent: If the performance of a system module degrades, its related normalized performance also degrades.

For regular-workload v-sensors, an additional step is needed for each specific v-sensor. Assume that a regular vsensoris executed three times in t0, t1, and t2, executing the same instruction sequence each time with different multiplicities m0, m1, and m2. Then, before comparing the execution time of each occurrence, we normalize each record with a factor of its multiplicity of execution mi that results in a normalized record ti=mi. A similar normalization process between different v-sensors is then performed, in which each v-sensor compares its records with the record that was most quickly normalized.

#### 6.3 History Comparison

VSENSOR tracks the collected performance-related data, such as wall time, and compares them with the given state of performance of the system to maintain a low overhead for analysis. The quantity of work is invariant for a v-sensor. We only keep a standard time scalar for each v-sensor but do not maintain a long list. We describe in Section 6.1 how each time slice has a record that indicates the execution time on average. Our tool transmits the standard execution time for each v-sensor to a normalized time compared with the fastest record. In addition to the execution time, we use a performance-monitoring unit (PMU [17]) to collect other metrics, including memory accesses and cache misses.

Note that VSENSOR can shut down the short-term v-sensor analysis to reduce overhead, which is to say that it can turn off the Tick and Tock function.

We illustrate the process of online detection in Fig. 19. We ran a v-sensor for 10 times, and collected the cache miss rate and wall time. We also use low and high to reflect the cache miss rates for the sake of simplicity. If it was invariant, we observed variance in records 2, 4, and 6 because of their relatively long durations. By contrast, the records were classified as high or low if the cache miss rate acted in a dynamic way. Based on this analysis, there were no data in the group representing variance in terms of a high cache miss rate, and record 4 had variance with a low cache miss rate.

![](_page_9_Figure_1.png)

Fig. 19. Online detection.

#### 6.4 Multiple Process Analysis

To analyze inter-procedure processes, VSENSOR builds an analysis server as a dedicated process. It compares the performance of a single sensor on various processes, and gathers performance-related information from every process to detect variance. The processes conduct these operations when they update shared files or communicate with the analysis server. Experiments have indicated that data transmission to the server is limited, and causes no significant network or IO degradation (detailed in Section 7). To further reduce the cost of analysis, each process keeps the data in a local buffer and transmits the collected data to the analysis server after they reach a certain threshold of size. In this way, it creates a suitable amount of batched messages that are network friendly.

#### 6.5 Performance Variance Report

We develop a visualizer to improve the interpretation of the results of predicted variance by users. For each category, such as the IO, network, and computation, our tool creates a performance matrix. We show an example of the performance matrix in Fig. 20, which displays the performance of 128 processes for 100 seconds.

The x-axis has a resolution of 200 ms, and reflects time. The MPI rank, which is the process ID, is represented by the y-axis. Colors are used to show degrees of variations in performance. For example, we indicate high performance in dark blue and low performance in whiter shades. We can see the variance in performance in the whiter part of this figure. Fig. 20 shows that the entire application generally exhibited high performance. In Section 7, we analyze the results of a significant difference in performance in empirical cases.

The white parts show the period and place of the variance in performance, and the type of variance indicates that aspect that incurred the variance. For instance, when the tool stated that certain processes were slower than others, this indicated that the nodes were possibly unstable. Our tool is equipped to identify variance in performance with a low overhead and minimal manual interference. Note that users should decide whether to perform a re-execution or reboot the system when VSENSOR detects a variance in performance and identifies bottlenecks.

## 7 EXPERIMENT

#### 7.1 Experimental Setup

Methodology. VSENSOR is implemented with LLVM version 3.5.0. We use ROSE, Dragonegg-3.5.0, and Clang-3.5.0 to Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

![](_page_9_Figure_12.png)

Fig. 20. Performance matrix example.

instrument codes. We use Python to implement the visualizer. Our current version can provide most functionalities described in previous sections, and they are discussed next. Benchmark. We use eight programs to measure the performance of VSENSOR, including five kernels SP, FT, CG, LU, and BT from the NAS Parallel Benchmarks (NPB) [18] and three real applications RAXML [19] AMG [20], and LULESH [21]. Platform. The evaluation was performed on the Tianhe-2A HPC supercomputer with an efficient and high-speed interconnected network. Each computing node contained two

Xeon E5-2692(v2) CPUs with 64 GB of memory. We used 4,096 processes in total.

In our evaluation, first, we use VSENSOR to detect fixedworkload v-sensors, verify the results, and analyze the runtime overhead of the algorithms used for detection. Second, we evaluate the benefits of regular v-sensors and external vsensors. Third, we analyze the capability of VSENSOR to identify the variance in performance. Finally, we focus on identifying variance in real cases on the Tianhe-2A HPC system.

#### 7.2 Overall Analysis of Fixed V-Sensors

We show the metrics used for analysis during compilation and runtime identification in Table 1. The left columns show the compile-time information and the right columns show the online results when using 4,096 MPI processes.

Our results include the types of v-sensors to instrument, numbers of observed v-sensors and snippets, and number of lines of code. We find that most v-sensors of instrumentation are computation sensors. The calls and loops are v-sensor candidates, as mentioned in Section 3.1. For instance, there are 4,695 candidates and 75K lines of code in AMG, and our tool observes 413 v-sensors among these snippets during compilation. However, it chooses only 71 v-sensors during the final instrumentation, which indicates that a large amount of snippets exhibiting variance in workload are filtered out to significantly reduce the instrumentation overhead.

We then check whether the workloads of the detected vsensors are invariant to verify the results. For example, we check the message sizes of the v-sensors of the network, and the results show that the arguments are fixed. The most difficult validation pertains to v-sensor identification, and we use the PMU to check if the workload has changed among iterations according to its number of instructions for the v-sensors used for computation. We provide each execution a vector of instructions, v0; v1; ...; vn. All the values are theoretically the same for a v-sensor. However, the sequence of vi has variance because the measurement of the PMU is not 100% accurate [22]. To measure the variation of the number of instructions, we define Ps ¼ MAXðviÞ=MINðviÞ to represent the variance of PMU data. Then, we calculate the maximum difference

Validation of Results of 4,096 MPI Processes with Fixed V-Sensors Program Code (KLoc) Number of snippets Number of v-sensors Instrumentation number and type Workload max error Performance overhead Sense-time coverage Frequency (kHz) BT 11.3 679 169 46Comp+1Net 2.7% 0.24% 4.3% 182.3 CG 2.0 214 50 6Comp+5Net 0.8% 2.02% 6.8% 0.493 FT 2.5 340 75 12Comp 3.3% 5.05% 7.7% 2.318 LU 7.7 1671 185 63Comp 2.2% 5.29% 70.9% 283.5 SP 6.3 697 149 37Comp+1Net 0.8% 0.90% 6.3% 1070 AMG 75.0 4695 413 65Comp+6Net 0.0% 0.08% 0.43% 0.010 LULESH 5.3 1671 103 22Comp+6Net 8.6% 4.15% 31.9% 3155 RAXML 36.2 4744 650 159Comp 2.3% 0.16% 14.3% 4530

TABLE 1

among all v-sensors with Pa ¼ MAXðPsÞ, and the maximum difference among all processes with Pm ¼ MAXðPaÞ. We show Pm 1 in the Workload max error column in Table 1. It is clear that our tool incurs an error of less than 9% on average, which shows its usability during compilation.

We compare the execution time of our tool with that of the original program execution to measure the performance cost incurred by the former. We execute the snippets several times and use the one with the shortest time owing to the large variance in performance on the Tianhe-2A HPC system. We show in Table 1 that the increase in the cost of performance is less than 6%, which proves the efficiency of VSENSOR during runtime.

In the two right columns of Table 1, the sense-time coverage and frequency are presented for each program. We denote the ratio of durations of all v-sensors to the total time as the sense-time coverage, and call the ratio of the number of v-sensors to the total time as the average frequency. Table 1 shows that these two metrics varied on different programs. For instance, LU has a v-sensor frequency of 283.5 kHz and a coverage of 70.9%, indicating that a v-sensor occurs at a 5-us interval on average, and most of the operational period of LU is monitored by VSENSOR. However, some programs, such as BT and AMG, have low coverage. The root issue is a lack of detectable fixed-workload vsensors in these programs, mainly the result of a dynamic workload in the computational pattern. We have shown in Section 7.3 and Section 7.4 that regular v-sensors and external v-sensors can further improve the coverage.

## 7.3 Analysis of Regular V-Sensors

We evaluate VSENSOR on regular v-sensors by using the same configuration as above. As shown in Fig. 21, the regular vsensors increase the average coverage by 14.3%. FT and SP show the most significant improvements of 38.5% and

![](_page_10_Figure_7.png)

Fig. 21. Coverage with or without regular workload v-sensors. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

35.0%, respectively, because they contain many loops with variable numbers of iterations that are identified as regular v-sensors. VSENSOR counts the number of iterations in the regular v-sensors and then divides the execution time of the loop to the number of iterations of the fixed-workload loop. Therefore, VSENSOR covers more execution time with the help of regular v-sensors. With both fixed and regular vsensors, the only program with less than 10% coverage is AMG. Even for programs with such dynamic computation patterns, we could use external v-sensors to improve the detection as described in Section 7.4.

Fig. 22 shows the overhead of fixed- and regular-workload v-sensors. After enabling regular v-sensors, applications besides the FT show a small performance penalty of 2.3% on average. FT has a large overhead due to a frequently invoked regular v-sensor. Most of the workload in FT consists of nested in-loops with non-constant loop conditions, and thus can be dealt with by fixed v-sensors. Although the overhead of the instrumented functions is small, the innermost loop might have comparable workloads in the body of the loop, and becomes a major source of overhead. It is worth noting that this extra overhead comes with non-trivial increments in sense-time coverage at the same time.

To maintain a small overhead, sampling is an effective method. We test FT with the 25% sampling rate. The results show it has an 11.5% performance overhead and 11.6% coverage. Sampling in VSENSOR is convenient because the sampling rate can be set at runtime. More complex sampling strategies can also be applied, such as adaptive sampling.

#### 7.4 External Analysis of V-Sensors

As Table 1 and Fig. 21 indicate, it is difficult to find internal v-sensors in AMG. We use external v-sensors to improve the coverage for this type of application. Section 5.2 analyzes the relation between the extra overhead and coverage in this case, and we have determined that low-coverage programs gain extra coverage with a smaller performance overhead than high-coverage programs. We evaluate 4,096 process AMG with 200-millisecond external v-sensors, and test it with 5%, 10%, 20%, and 30% target coverage.

Fig. 23 shows the results of AMG with external v-sensors. The ideal coverage line coincides with the real coverage in this figure. This verifies that VSENSOR achieves the target coverage under these four configurations. The real overhead is consistent with the theoretical values under small coverage target. However, it is higher than the theoretical value under

![](_page_11_Figure_1.png)

Fig. 23. AMG results with external v-sensors.

a high coverage target. This extra overhead is resulted from the dependence among processes. Furthermore, the extended execution time leads to more external v-sensor invocations as well. This introduces more performance overhead but is still necessary because VSENSOR tries to reach the target coverage during the whole execution.

#### 7.5 V-Sensor Distribution

We analyze the distribution of v-sensors because the performance of VSENSOR is influenced by their temporal characteristics. We show the main concepts pertaining to the distribution of v-sensors in Fig. 16, where the length of the v-sensor is called duration, and the distance between consecutive v-sensors is called interval.

We group the v-sensors into four categories based on execution time: (1) longer than 1s, (2) 1ms to 1s, 3) 100us to 10ms, and 4) less than 100us. We show the execution intervals in Figs. 24 and 25 for each case.

We omit the plotting of case longer than 1s because only one network v-sensor is used in all evaluations. Most sensetimes are shorter than 100us, which shows that the aggregation is necessary as shown in Section 6.1, and most v-sensors belong to fine-grained snippets.

We can guarantee that VSENSOR detects variance in performance that is longer than 1s because most intervals are shorter than 1s. However, some programs include intervals longer than 1s. For example, in RAXML, many I/O operations are invoked that last for a long time on a distributed file system. However, VSENSOR is still able to observe such variances in performance because of a large amount of v-sensors across the code. By contrast, for AMG, there are long durations without v-sensors that exist only for a small duration of the entire execution. Table 1 shows its low frequency and coverage, which are caused by the adaptive algorithm of mesh refinement. Because this can lead to changes in workload on the fly, only some fixed snippets of workloads exist in this situation. Furthermore, VSENSOR cooperates well with Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply.

![](_page_11_Figure_9.png)

![](_page_11_Figure_10.png)

![](_page_11_Figure_11.png)

Fig. 25. The intervals between v-sensors.

a large amount of HPC applications with static workloads, and the external v-sensors are able to deal with the remaining programs.

#### 7.6 Injecting Noise

We manually provide an instance of the injection of noise to the 128-process cg.D.128 benchmark in NPB with the help of the mpiP [23] profiler and VSENSOR. However, we conduct this experiment only locally on a dual Xeon E5-2670(v3) cluster with a 100 Gbps 4EDR InfiniBand because of the challenges of operating the Tianhe-2A HPC system.

Compared with Profiling. We show the results of mpiP in Fig. 26 for a regular execution with no noise injection. The computation and communication times are around 75s and 50s, respectively. The profiling is unable to justify the short time difference between processes due to variance among compute nodes or workloads. We then inject noise and execute the code again as follows: During the program execution, some nodes start to execute noiser, and the program competes for resources such as memory and CPU with noiser. The noise is injected twice, each for 10s. The performance degrades with such injections.

We show the results of a profile with mpiP in Fig. 27 after injecting noise. In contrast to Fig. 26, the time needed to execute MPI increases from around 50s to around 65s, but the time needed for computation remains the same. We are unable to determine whether the variance has an influence on the program when using only Fig. 27. Because of the greater amount of MPI communication, it is not easy to analyze network issues. We manage to provide a reasonable analysis for the CG in such situations when analyzing the code and the results of mpiP: Because the CPUs have more idle time between instances of communication, our tool could inject the workload between MPI calls. Therefore, the communication is delayed significantly for some processes and the tool stretches little computation. The performance-degrading

![](_page_12_Figure_1.png)

Fig. 26. mpiP results for a regular execution.

![](_page_12_Figure_3.png)

Fig. 27. Profiling a noise-injected execution with mpiP.

processes incur long waiting times in communication, and mpiP regards this as MPI time. Moreover, such a technique should be popular among non-expert users of MPI.

It is unable to locate the noise injected from mpiP, and VSENSOR can make up for this deficiency. Fig. 20 shows the performance matrix of a regular execution, and Fig. 28 shows white two blocks representing the injected noise. It shows that processes 24 to 47 and 72 to 96 are injected with noise at around 34s and 66s, respectively. Therefore, VSENSOR exhibits extra benefit in terms of identifying variance in performance compared with typical profilers.

Compared with Tracing. To perform further analysis, an external MPI tracer, ITAC [24], is used to gather traces. Compared with the sizes of the result obtained by VSENSOR, 8.8 MB, ITAC creates a larger result, 501.5 MB. This is because in empirical applications, the tools for analysis based on traces can generate a large amount of data that result in an overhead in terms of time and memory. However, VSENSOR can handle such difficulties plaguing previous tools. In this execution, the generated size of the data for 128 processes within 140s is only 8.8 MB, which means that for each process, the rate for generation is about 0.5 KB/s. Accordingly, for 16,384 processes, the total generation rate is only 8 MB/s, and occupies a small portion of network communication.

#### 7.7 Comparison With Benchmarking, Profiling, Tracing, and Performance Model

We compare VSENSOR with other methods in terms of performance and storage overhead. Five programs from NPB benchmarks (BT, CG, FT, LU, SP) are evaluated using 256 processes with C-scale problem size. Each node in the cluster has dual 12-core Intel E5-2670 v3 processors. As shown in Fig. 29, we choose a popular profiling tool HPCToolkit [25] for comparison. Although profiling erases detailed timedimension information and cannot locate when variance happens, it still introduces much more time and storage overhead than VSENSOR. We conduct function-level tracing with Scalasca [12]. It introduces prohibitive performance overhead and generates more than 1GB data on average.

![](_page_12_Figure_10.png)

Fig. 28. Results of a noise-injected execution with VSENSOR.

![](_page_12_Figure_12.png)

Fig. 29. Average Performance overhead and storage on 256-process Cscale NPB benchmarks of profiling (HPCToolkit), tracing (Scalasca), tracing with sampling, and VSENSOR. OOR means out of range.

Although sampling improves its performance, average performance overhead still reaches 27.0%. Hence, tracing is not suitable in a production environment to detect performance variance. VSENSOR has the least performance and storage overhead. Compared with VSENSOR, the limitation of these methods on variance detection is twofold.

First, online detecting variance with these methods is challenging due to the lack of v-sensors. With v-sensors, VSENSOR detects variance based on intra- and inter-process comparison within a single run of applications. VSENSOR is able to locate when and where variance happens and quantify its influence, while other methods cannot.

- Running extra benchmarks periodically not only wastes computation resources but also misses performance variance when benchmarks are not being executed. Furthermore, applications usually use different resources and have different requirements from benchmarks during the execution, which makes a single benchmark fail to detect all variances of the application.
- Tracing and profiling are workload-agnostic, so collected performance data are not directly comparable if corresponding workloads are different. To detect variance, these approaches need to run programs twice and analyze the difference between them, such as the mpiP case in Section 7.7. Due to the lack of vsensors, they are not suitable for online variance detection.
- Accurate performance models predict the execution time of a program. Performance variance can be identified by comparing predicted performance and measured performance. Unfortunately, most performance models can only estimate the overall performance variance, but fail to identify where such variance comes.

Second, these approaches require extra performance overhead or human efforts to detect variance, which is unacceptable in production environment.

![](_page_13_Figure_1.png)

- Running extra periodical benchmarks to detect variance is intrusive, which competes for computation resources with applications and hurts applications' performance.
- Tracing introduces large overhead and generates a large volume of trace data. A function-level tracing XRay incurs 20-40% overhead for common programs [26]. On contrary, VSENSOR incurs less than 6% overhead on average and provides detailed information about performance variance.
- Accurate performance models normally require huge human efforts, as it is not portable. A model built for one application usually cannot achieve accurate prediction results for another application. Moreover, applying models to different platforms requires modifying the model as well. On contrary, VSENSOR can automatically analyze and instrument applications, as well as the instrumented applications can be used on any platform.

#### 7.8 Case Studies

In this section, we show how to use VSENSOR to identify the variance in performance on the Tianhe-2A HPC system. We use CG as an example, and show its computational performance using 256 processes in Fig. 30.

A white line appears close to process 100 above, indicating that it slows the execution. VSENSOR can accurately detect the problematic processes; if they are on the same node, the host node needs to be replaced. To confirm this idea, we use micro-benchmarks to check the system's performance, including memory and CPU. Our results show that CPU performance is normal, but the memory-related performance of one processor is only 55% of that of the other nodes. Such information is reported to system administrator, and we use another node to replace it for re-execution. When the problematic node is replaced, the execution time of CG is optimized to 66.05s, from the original time of 80.04s. We get an improvement of 21%.

Although a pre-test before the execution of the application can solve this problem of variance in performance, the same nodes still can exhibit variance during execution, as illustrated in Fig. 1. For instance, we execute FT with 1,024 processes on a fixed cluster to observe the variance in performance during program execution, while a traditional pre-test cannot handle this issue.

Fig. 1 illustrates that the time for an FT execution is 23.31s, and in an abnormal case can reach 78.66s, slowing down by 3:37 times. Our tool can identify the variance in performance, as shown in the performance matrix of the network in Fig. 31. It shows that a degradation in performance occurs from 16s to 67s. After further checking the

![](_page_13_Figure_11.png)

Fig. 30. Results generated by VSENSOR for CG. Fig. 31. Results generated by VSENSOR for FT.

code for FT, we find that it exchanges data between processes through MPI_Alltoall. This is because MPI_Alltoall needs to cooperate with all processes, which is very complicated in communication among networks. Furthermore, we observe that the Tianhe-2A HPC system sometimes encounters problems in performance due to the variance in the performance of FT. Such network problems may be due to network congestion, which cannot be prevented. However, VSENSOR can report such issues, and leave the choice of whether to continue to users.

As shown in this section, VSENSOR detects resource contentions, memory faults, and network performance problems. Besides these performance variances, VSENSOR can detect other variances resulting from external environments, such as OS noises and IO device problems. Since these problems make the execution time of fixed-workload benchmarks varies, VSENSOR is able to detect these performance variances by monitoring v-sensors.

## 8 DISCUSSIONS

Integration with Production Environment. Since VSENSOR focuses on performance variance caused by external environment, both developers and administrators should care about these problems. Developers can use VSENSOR to detect performance variance and try to avoid them in program executions. System administrators can use our system to detect system abnormalities such as hardware faults. In this work, we focus on the methodology of variance detection and verify the effectiveness of v-sensors. We implement it as a performance tool. However, this method is promising to be integrated with production environment as a longterm service and we leave it as our future work.

Requirements of VSENSOR. As a performance tool relies on static analysis, VSENSOR requires source code of applications. VSENSOR is impractical for closed-source applications and libraries. VSENSOR may miss fixed-workload snippets that cannot be determined at compilation time but can be only confirmed at runtime. To solve this problem, combining more runtime information is a potential solution. We leave it as our future work.

# 9 RELATED WORK

Performance Variance. Variance in performance is a very important problem in current HPC systems [3], [7], [27], [28], [29], [30], [31]. Skinner et al. [27] studied the variance in performance among HPC systems and pointed out the performance improvement without variance in performance. Hoefler et al. [7] explored the variance in operating systems of HPC applications, and concluded that the pattern of variance has a larger influence than its intensity. Tsafrir et al. Authorized licensed use limited to: UNIVERSITY OF DELAWARE LIBRARY. Downloaded on November 25,2024 at 19:09:07 UTC from IEEE Xplore. Restrictions apply. [28] showed that the interrupts of the periodic clock cause a major variance in general operating systems; OS co-scheduling can be a solution to this problem [29].

Agarwal et al. [32] explored performance distributions in scalable parallel programs, and pointed out that long-tail noise can incur a significant degradation in performance. Ferreira et al. [2] injected different noises into programs in HPC systems and studied their influence. Beckman et al. [33] demonstrated the synchronization overhead caused by system interrupts, and Phillips et al. [34] showed that daemon processes can prevent nodes from performing efficient computations in HPC systems.

Variance Detection. Previous studies have applied models to identify variance in performance [1], [35], [36], [37], [38], [39]. Petrini et al. [1] used analytic models to detect performance problems for SAGE on HPC systems. This can be used to quantify the influence of system noise on performance. Lo et al. [35] built a general toolkit to analyze architectural variance by the roofline model [36]. Many researchers, such as Calotoiu [37], Yeom [38], and Lee [39], have examined accelerating model constructing; however, we find many unsolved problems in the context of constructing a suitable model for large-scale HPC applications.

Jones et al. [9] analyzed the traces of systems to find reasons for variance in performance, but the size of the trace could be large when the problem size was large [11]. Trace collection can incur a significant degradation in the performance of applications [13], [40]; thus, accurate noise identification is impractical in HPC systems. Caliper [41] is an efficient performance data collection framework that can be integrated into our performance variance detection. Statistical tracers [42] and profilers [23] are light-weight choices, but are less accurate.

Our tool, VSENSOR, focuses on variance in system performance; other tools like PRODOMETER [43], AutomaDeD [44], and STAT [45], focus on the bug detection and program faults, and are different from our tool. PerfScope [46] analyzed system call invocations to identify potential buggy functions. Sahoo et al. [47] monitored program invariants to find software bugs.

Overall, previous works have been unable to efficiently identify variance in performance on the fly in a light-weight manner, whereas VSENSOR uses features of the program that integrates both dynamic and static detection technologies to efficiently identify variance in performance.

## 10 CONCLUSION

We propose a light-weight tool, called VSENSOR, which is able to detect variance in the performance of systems on the fly. We can obtain features of online program execution directly from the code without relying on an external detector. In particular, we show that there are repeated snippets executed with a fixed quantity of work for a large number of HPC programs. Our tool automatically identifies the snippets of static workloads via complication technologies and regards them as v-sensors to evaluate performance. We validate VSENSOR on the Tianhe-2A HPC system, and results show that it incurs a performance cost of less than 6% with 4,096 processes for fixed v-sensors. Specifically, it can identify nodes that have slow memory, and improve performance by 21%. Furthermore, it identifies a serious bottleneck in the network that slows performance by 3:37 .

# ACKNOWLEDGMENTS

We would like to thank the anonymous reviewers for their insightful comments.

# REFERENCES

- [1] F. Petrini, D. J. Kerbyson, and S. Pakin, "The case of the missing supercomputer performance: Achieving optimal performance on the 8,192 processors of ASCI Q," in Proc. ACM/IEEE Conf. Supercomput., 2003, pp. 55–55.
- [2] K. B. Ferreira, P. G. Bridges, R. Brightwell, and K. T. Pedretti, "The impact of system design parameters on application noise sensitivity," in Proc. IEEE Int. Conf. Cluster Comput., 2013, pp. 117–129.
- [3] O. H. Mondragon, P. G. Bridges, S. Levy, K. B. Ferreira, and P. Widener, "Understanding performance interference in next-generation HPC systems," in Proc. Int. Conf. High Perform. Comput., Netw., Storage Anal., 2016, pp. 384–395.
- [4] N. J. Wright, S. Smallen, C. M. Olschanowsky, J. Hayes, and A. Snavely, "Measuring and understanding variation in benchmark performance," in Proc. DoD High Perform. Comput. Modernization Prog. Users Group Conf., 2009, pp. 438–443.
- [5] top500 website, 2017. [Online]. Available: http://top500.org/
- [6] D. Skinner and W. Kramer, "Understanding the causes of performance variability in HPC workloads," in Proc. IEEE Int. Workload Characterization Symp., 2005, pp. 137–149.
- [7] T. Hoefler, T. Schneider, and A. Lumsdaine, "Characterizing the influence of system noise on large-scale applications by simulation," in Proc. ACM/IEEE Int. Conf. High Perform. Comput., Netw., Storage and Anal., 2010, pp. 1–11.
- [8] Y. Gong, B. He, and D. Li, "Finding constant from change: Revisiting network performance aware optimizations on iaas clouds," in Proc. Int. Conf. High Perform. Comput., Netw., Storage Anal., 2014, pp. 982–993.
- [9] T. Jones, L. Brenner, and J. Fier, "Impacts of operating systems on the scalability of parallel applications," Lawrence Livermore Nat. Lab., Tech. Rep., 2003.
- [10] N. R. Tallent, L. Adhianto, and J. M. Mellor-Crummey , "Scalable Identification of Load Imbalance in Parallel Executions Using Call Path Profiles," in Proc. ACM/IEEE Int. Conf. High Perform. Comput., Netw., Storage Anal., 2010, pp. 1–11.
- [11] B. J. N. Wylie, M. Geimer, and F. Wolf, "Performance measurement and analysis of large-scale parallel applications on leadership computing systems," Sci. Prog., vol. 16, no. 2/3, pp. 167–181, Apr. 2008.
- [12] M. Geimer, F. Wolf, B. J. Wylie, E. Abrah am, D. Becker, and B. Mohr, "The scalasca performance toolset architecture," Concurrency Comput. Pract. Experience, vol. 22, no. 6, pp. 702–719, 2010.
- [13] J. Zhai, J. Hu, X. Tang, X. Ma, and W. Chen, "Cypress: Combining static and dynamic analysis for top-down communication trace compression," in Proc. Int. Conf. High Perform. Comput., Netw., Storage Anal., 2014, pp. 143–153.
- [14] F. Zhang, J. Zhai, X. Shen, O. Mutlu, and X. Du, "POCLib: A High-Performance Framework for Enabling Near Orthogonal Processing on Compression," IEEE Trans. Parallel Distrib. Syst., vol. 33, no. 2, pp. 459–475, Feb. 2022.
- [15] C. Lattner and V. Adve, "LLVM: A compilation framework for lifelong program analysis & transformation," in Proc. Int. Symp. Code Gener. Optim., Feedback-Directed Runtime Optim., 2004, Art. no. 75.
- [16] MPI Documents, 2016. [Online]. Available: http://mpi-forum. org/docs/
- [17] P. Mucci, J. Dongarra, S. Moore, F. Song, F. Wolf, and R. Kufrin, "Automating the large-scale collection and analysis of performance data on Linux clusters1," in Proc. 5th LCI Int. Conf. Linux Clusters. HPC Revolution, 2004, pp. 1–24.
- [18] D. Bailey, T. Harris, W. Saphir, R. V. D. Wijngaart, A. Woo, and M. Yarrow, "The NAS Parallel Benchmarks 2.0," NAS Systems Division, NASA Ames Research Center, Moffett Field, CA, USA, Tech. Rep. NAS-95–020, 1995.
- [19] W. Pfeiffer and A. Stamatakis, "Hybrid MPI/pthreads parallelization of the RAxML phylogenetics code," in Proc. IEEE Int. Symp. Parallel Distrib. Process., Workshops Phd Forum, 2010, pp. 1–8.

- [20] U. M. Yang et al., "BoomerAMG: A parallel algebraic multigrid solver and preconditioner," Appl. Numer. Math., vol. 41, no. 1, pp. 155–177, 2002.
- [21] I. Karlin et al., "Lulesh programming model and performance ports overview," Lawrence Livermore National Lab., Livermore, CA, USA, Tech. Rep. LLNL-TR-608824, Dec. 2012.
- [22] V. M. Weaver, D. Terpstra, and S. Moore, "Non-determinism and overcount on modern hardware performance counter implementations," in Proc. IEEE Int. Symp. Perform. Anal. of Syst. Softw., 2013, pp. 215–224.
- [23] J. Vetter and C. Chambreau, "mpiP: Lightweight, scalable MPI profiling," 2021. [Online]. Available: https://github.com/ LLNL/mpiP
- [24] Intel trace analyzer and collector, 2017. [Online]. Available: https://software.intel.com/en-us/intel-trace-analyzer
- [25] L. Adhianto et al., "HPCTOOLKIT: Tools for performance analysis of optimized parallel programs," Concurrency Comput. Pract. Experience, vol. 22, no. 6, pp. 685–701, 2010.
- [26] D. M. Berris, A. Veitch, N. Heintze, E. Anderson, and N. Wang, "XRay: A function call tracing system," Tech. Rep., 2016.
- [27] D. Skinner and W. Kramer, "Understanding the causes of performance variability in HPC workloads," in Proc. IEEE Int. Workload Characterization Symp., 2005, pp. 137–149.
- [28] D. Tsafrir, Y. Etsion, D. G. Feitelson, and S. Kirkpatrick, "System noise, os clock ticks, and fine-grained parallel applications," in Proc. 19th Annu. Int. Conf. Supercomput., 2005, pp. 303–312.
- [29] T. Jones, "Linux kernel co-scheduling and bulk synchronous parallelism," Int. J. High Perform. Comput. Appl., vol. 26, pp. 136–145, 2012.
- [30] F. Zhang, J. Zhai, B. He, S. Zhang, and W. Chen, "Understanding co-running behaviors on integrated CPU/GPU architectures," IEEE Trans. Parallel Distrib. Syst., vol. 28, no. 3, pp. 905–918, Mar. 2017.
- [31] Z. Pan et al., "Exploring data analytics without decompression on embedded GPU systems," IEEE Trans. Parallel Distrib. Syst., vol. 33, no. 7, pp. 1553–1568, Jul. 2022.
- [32] S. Agarwal, R. Garg, and N. K. Vishnoi, "The impact of noise on the scaling of collectives: A theoretical approach," in Proc. 12th Int. Conf. High Perform. Comput., 2005, pp. 280–289.
- [33] P. Beckman, K. Iskra, K. Yoshii, and S. Coghlan, "The influence of operating systems on the performance of collective operations at extreme scale," in Proc. IEEE Int. Conf. Cluster Comput., 2006, pp. 1–12.
- [34] J. C. Phillips, G. Zheng, S. Kumar, and L. V. Kale, "NAMD: Biomolecular simulation on thousands of processors," in Proc. Supercomput. ACM/IEEE Conf., 2002, p. 36–36.
- [35] Y. J. Lo et al., "Roofline model toolkit: A practical tool for architectural and program analysis," in Proc. Int. Workshop Perform. Model. Benchmarking Simul. High Perform. Comput. Syst., 2014, pp. 129–148.
- [36] S. Williams, A. Waterman, and D. Patterson, "Roofline: An insightful visual performance model for multicore architectures," Commun. ACM, vol. 52, no. 4, pp. 65–76, 2009.
- [37] A. Calotoiu et al., "Fast multi-parameter performance modeling," in Proc. IEEE Int. Conf. Cluster Comput., 2016, pp. 172–181.
- [38] J.-S. Yeom, J. J. Thiagarajan, A. Bhatele, G. Bronevetsky, and T. Kolev, "Data-driven performance modeling of linear solvers for sparse matrices," in Proc. Int. Workshop Perform. Model., Benchmarking Simul. High Perform. Comput. Syst., 2016, pp. 32–42.
- [39] S. Lee, J. S. Meredith, and J. S. Vetter, "COMPASS: A framework for automated performance modeling and prediction," in Proc. 29th ACM Int. Conf. Supercomput., 2015, pp. 405–414.
- [40] X. Wu and F. Mueller, "Elastic and scalable tracing and accurate replay of non-deterministic events," in Proc. 27th Int. ACM Conf. Int. Conf. Supercomput., 2013, pp. 59–68.
- [41] D. Boehme et al., "Caliper: Performance introspection for HPC software stacks," in Proc. Int. Conf. High Perform. Comput., Netw., Storage Anal., 2016, pp. 550–560.
- [42] N. R. Tallent, J. Mellor-Crummey , M. Franco, R. Landrum, and L. Adhianto, "Scalable fine-grained call path tracing," in Proc. Int. Conf. Supercomput., 2011, pp. 63–74.
- [43] S. Mitra, I. Laguna, D. H. Ahn, S. Bagchi, M. Schulz, and T. Gamblin, "Accurate application progress analysis for large-scale parallel debugging," ACM SIGPLAN Notices, vol. 49, no. 6, pp. 193–203, 2014.
- [44] I. Laguna, D. H. Ahn, B. R. de Supinski, S. Bagchi, and T. Gamblin, "Diagnosis of performance faults in largescale MPI applications via probabilistic progress-dependence inference," IEEE Trans. Parallel Distrib. Syst., vol. 26, no. 5, pp. 1280–1289, May 2015.

- [45] D. C. Arnold, D. H. Ahn, B. De Supinski, G. Lee, B. Miller, and M. Schulz, "Stack trace analysis for large scale applications," in Proc. 21st IEEE Int. Parallel Distrib. Process. Symp., 2007, pp. 1–10.
- [46] D. J. Dean et al., "PerfScope: Practical online server performance bug inference in production cloud computing infrastructures," in Proc. ACM Symp. Cloud Comput., 2014, pp. 1–13.
- [47] S. K. Sahoo, J. Criswell, C. Geigle, and V. Adve, "Using likely invariants for automated software fault localization," in Proc. 18th Int. Conf. Architectural Support Prog. Lang. Oper. Syst., 2013, pp. 139–152.

![](_page_15_Picture_29.png)

Jidong Zhai received the BS degree in computer science from the University of Electronic Science and Technology of China, Chengdu, China, in 2003, and the PhD degree in computer science from Tsinghua University, Beijing, China, in 2010. He is currently an associate professor with the Department of Computer Science and Technology, Tsinghua University. His research interests include performance evaluation for high performance computers, performance analysis, and modeling of parallel applications.

![](_page_15_Picture_31.png)

Liyan Zheng received the BS degree in computer science from Tsinghua University, Beijing, China, in 2020. He is currently working toward the PhD degree with the Institute of High-Performance Computing, Tsinghua University. His research interests include performance variance diagnosis for large-scale applications, performance analysis for parallel HPC programs, and optimizations of machine learning systems.

![](_page_15_Picture_33.png)

Jinghan Sun received the BS degree in computer science from Beihang University in 2018 and the MS degree in computer science from the University of Illinois at Urbana-Champaign in 2020. He is currently working toward the PhD degree with the Department of Computer Science, the University of Illinois at Urbana-Champaign. His research interests include high-performance computing, fault-tolerant storage systems, and machine learning for systems.

![](_page_15_Picture_35.png)

Feng Zhang received the bachelor's degree from Xidian University in 2012, and the PhD degree in computer science from Tsinghua University in 2017. He is currently an associate professor with DEKE Lab and School of Information, Renmin University of China. His research interests include database systems, and parallel and distributed systems.

![](_page_15_Picture_37.png)

Xiongchao Tang received the BS and PhD degrees from Tsinghua University in 2013 and 2019, respectively. He is currently a postdoctoral with Tsinghua Shenzhen International Graduate School and Sangfor Technologies Inc. His research interests include performance analysis and performance optimization for multi-core systems and large-scale clusters.

![](_page_16_Picture_1.png)

Xuehai Qian received the PhD degree from the Computer Science Department, University of Illinois at Urbana-Champaign. He is currently an assistant professor with the Ming Hsieh Department of Electrical Engineering and the Department of Computer Science, University of Southern California. His research interests include computer architecture and architectural support for programming productivity and correctness of parallel programs.

![](_page_16_Picture_3.png)

Wenguang Chen received the BS and PhD degrees in computer science from Tsinghua University, in 1995 and 2000, respectively. He was the CTO with Opportunity International Inc. from 2000-2002. Since January 2003, he joined Tsinghua University. He is currently a professor and associate head with the Department of Computer Science and Technology, Tsinghua University. His research interests include parallel and distributed computing and programming model.

![](_page_16_Picture_5.png)

Bingsheng He received the PhD degree from the Hong Kong University of Science & Technology in 2008. He is currently an associate professor with the Department of Computer Science, National University of Singapore (NUS). Before joining NUS in May 2016, he was a researcher with System Research Group, Microsoft Research Asia from 2008 to 2010, and a faculty member with Nanyang Technological University, Singapore. His research interests include Big Data management, parallel and distributed systems, and cloud computing.

![](_page_16_Picture_7.png)

Weimin Zheng received the BS and MS degrees from Tsinghua University, China, in 1970 and 1982, respectively. He is currently a professor with the Department of Computer Science and Technology, Tsinghua University. His research interests include distributed computing, compiler techniques, and network storage. He is an academician of the Chinese Academy of Engineering.

![](_page_16_Picture_9.png)

Wei Xue is currently an associate professor with the Department of Computer Science and Technology, Tsinghua University, China. He is the director with High Performance Computing Institute, Tsinghua and a joint faculty with the Department of Earth System Science, Tsinghua. His research interests include scientific computing, performance evaluation and optimization, and uncertainty quantification. As one of team leaders, he received the 2016 and 2017 Gordon Bell Prizes and finalist of 2018 Gordon Bell Prize.

" For more information on this or any other computing topic, please visit our Digital Library at www.computer.org/csdl.

