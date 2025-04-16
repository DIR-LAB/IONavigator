![](_page_0_Picture_1.png)

# Characterizing and Mitigating the I/O Scalability Challenges for Serverless Applications

Rohan Basu Roy, Tirthak Patel, Devesh Tiwari Northeastern University

2021 IEEE International Symposium on Workload Characterization (IISWC) | 978-1-6654-4173-5/21/$31.00 ©2021 IEEE | DOI: 10.1109/IISWC53511.2021.00018

*Abstract*—As serverless computing paradigm becomes widespread, it is important to understand the I/O performance characteristics on serverless computing platforms. To the best of our knowledge, we provide the first study that analyzes the observed I/O performance characteristics – some expected and some unexpected findings that reveal the hidden, complex interactions between the application I/O characteristics, the serverless computing platform, and the storage engines. The goal of this analysis is to provide data-driven guidelines to serverless programmers and system designers about the performance trade-offs and pitfalls of serverless I/O.

#### I. INTRODUCTION

Background and Motivation. Serverless computing is bringing a significant paradigm shift in how programmers program their applications and end-users utilize the computing resources – similar to the effect that the emergence of cloud computing had almost a decade ago [58], [25], [46], [1], [38], [32]. Major cloud computing providers are already offering serverless computing platforms to end-users. Computer system researchers are beginning to utilize these resources to better understand the capabilities, limitations, and characteristics of the serverless computing model, albeit mostly focused on the compute and memory aspects [36], [37], [30], [65], [73], [53], [52]. The I/O aspect has received limited attention, but that is anticipated to change quickly [79], [68].

A key feature of serverless computing is that tasks are stateless and they need to communicate via a remote storage. Consequently, a majority of serverless I/O and storage studies have focused on building efficient and practical ephemeral storage capabilities to transfer intermediate data among tasks in multi-task analytics jobs [44], [43]. But, the research community lacks an easily-accessible, systematic, and sufficiently detailed experimental evaluation to characterize the I/O performance of serverless applications – an area that is beginning to grow and receive rich I/O support from vendors such as Amazon AWS, Google Cloud, Microsoft Azure, and IBM Cloud [71], [79], [60], [54], [23], and new solutions including ephemeral serverless storage, using serverless temporary storage as cache, smarter locality-enhanced serverless scheduling, function caching, etc. [43], [44], [79], [11], [26].

Serverless computing platforms are now beginning to provide I/O-rich support for serverless applications. For example, S3 was the only storage engine option available on the AWS Lambda platform to end-users (Amazon's serverless platform). Only recently EFS was added as another storage engine option to AWS Lambda [9]. However, currently, there is no study that performs a systematic experimental evaluation of the available storage options and quantifies the trade-offs. Furthermore, understanding and quantifying the I/O performance, especially at a high concurrency level, in serverless computing model remains unexplored (the focus of this paper). Serverless computing naturally provides a very high level of concurrency at a cheaper cost, almost instantaneously, and without the burden of provisioning and managing computing resources.

Contributions. To the best of our knowledge, *this is the first experimental study that characterizes the I/O performance and behavior of several I/O-intensive serverless applications on a commercially-provided serverless computing platform (AWS Lambda)*. In particular, we conducted an experimental campaign on AWS Lambda serverless platform to quantify and characterize the I/O component of three widely-used serverless applications (a neural network-based image recognition, sorting algorithm, and video analytics [81], [59], [43]). AWS provides one of the most widely-used and highest performant serverless computing platforms, competitive technical support, and best flexibility with I/O offerings.

*Our study reveals that on the serverless platform, serverless applications observe significantly different I/O performance depending upon the storage engine attached to it (e.g., Amazon object-based S3 storage, Amazon Elastic File System)*. The observed characteristics are more complicated and nuanced than widely-held expectations such as "latest capability is the best" and "faster option is always better". The conventional wisdom when using Amazon Elastic Computing Cloud (EC2) instances is that EFS tends to be faster than S3 [41]. But, we found that the preferred storage engine (EFS vs. S3) heavily depends on whether the serverless application is read-intensive or write-intensive due to underlying AWS Lambda and EFS interactions (Sec. IV). The magnitude of performance difference between EFS and S3 can be significant – more than 2× difference in the read performance and up to 1.5× difference in the write performance. Furthermore, our experiments reveal that the storage engine with faster average I/O performance is not necessarily the optimal choice if the application's figure of merit is I/O tail latency instead of median latency.

*One of the surprising revelations of our study is that serverless applications using Amazon EFS can experience I/O performance degradation at a high degree of concurrency, where multiple serverless functions perform I/O concurrently*.

![](_page_1_Figure_0.png)

Fig. 1: *Overview of our methodology for running multiple invocations of the benchmarks on AWS Lambda with storage.*

Serverless computing is designed to enable users to quickly launch hundreds of tasks with high elasticity. But, unfortunately, this capability is sub-optimal when applications are in the I/O phase, increasing computing risk and financial loss.

To mitigate the above challenges, we experimented with various pay-more-for-better-I/O-performance strategies from the cloud computing provider, but we discovered that they may not always work as desired for different use cases, which is expected since cloud computing providers cannot provide optimal solutions for all use cases, and users should leverage the existing functionalities to design their own solutions.

Therefore, *we developed home-grown remedies to mitigate the observed I/O challenges and devised a simple yet effective approach of "staggering the function invocations"*. Instead of launching all the invocations together, a simple strategy of batching the invocations with interleaved artificial delays can be surprisingly effective at improving both the I/O performance and overall turnaround time despite the delay in starting the Lambda invocations (Sec. IV).

In the context of recent works, in the emerging area of serverless I/O [79], [11], [68], [43], [44], [63], [84], our study confirms some findings from previous studies that I/O is critical for high performance in serverless computing model, even though the serverless application might be performing sequential I/O [81], [59], [43]. However, unlike previous studies [43], [44], [63], [84], it reveals multiple new interesting and alarming trends including: the I/O bottleneck is particularly severe at a high concurrency level, the I/O performance has a long tail latency, and these trends are dependent on whether an application is read-intensive or write-intensive, and which storage engine (EFS vs. S3) is being employed. *Our experimental artifact is available at: https://zenodo.org/record/5539888.*

#### II. SERVERLESS BACKGROUND

Serverless computing model (also known as "Function-asa-Service") raises the abstraction of computing by requiring the users to only develop and deploy the "function", and not be concerned about the back-end details (e.g., what hardware type to choose, how to appropriately provision and scale the compute capacity when the load changes, and what VM/OS to choose.). In this model, the user creates an *application deployment package* (referred to as a *serverless function*) that includes the application logic along with its associated dependencies and ships it to the cloud provider. Once a function is invoked by a user, its corresponding container is spawned in a VM by the cloud provider (e.g., Amazon's Firecracker micro VM).

The main advantage of serverless computing model is that the cost and overhead of managing the underlying computing resources is significantly lower and the user is responsible only for paying for what is actually used. On the downside, users of serverless computing do not have control over where their functions gets executed and often have restrictions about the resources a function execution can consume. For example, in Amazon Lambda serverless computing model, a function cannot execute for more than 900 seconds and can not consume more than 10 GB of memory. Every single second is critical for serverless applications since the execution is terminated at the 900 seconds threshold (e.g., an slow output writing phase at the end of the application can potentially waste the whole run if it does not finish by the 900 seconds deadline.).

Restricting the compute and storage resource consumption allows the cloud provider to better provision and manage resources of function executions from different users without exposing the infrastructure-level details to the users. However, there are many ongoing efforts to work around these limitations to make serverless computing more attractive for a wide variety of applications [80], [24], [64]. While the storage and I/O management of serverless computing platform received little attention so far, and we believe it will grow as a research area [79], [44], [43]. As serverless computing becomes more mainstream, its storage and I/O management aspects will need to be better understood and designed.

Storage and I/O in Serverless Computing. Due to restrictions on code deployment package size, users cannot use the deployment package for reading sizeable input data. They need to read the input from an external storage medium. Unfortunately, because the serverless functions are *stateless* and cannot be accessed directly after they complete their execution, the output produced by these functions also needs to be written to the external storage. These (slow) external storage systems become the only medium to transfer state across stateless function invocations.

AWS Lambdas are able to access two types of external storage: Amazon Simple Storage Service (S3) and Elastic File System (EFS). S3 is a virtual key-value object storage. When the data is stored, it is assigned a key (used to fetch the data). A new object is created for every write and re-write. While this option works well for some applications, it does not have the directory structure, customization options, and the multi-user security features of a file system.

To fill that gap, AWS introduced the feature of accessing EFS from Lambdas (June 2020 [9]). Once a VM is allocated for a serverless function, EFS gets mounted to it using the Network File System (NFS version 4.0) protocol with a fixed buffer size of 4KB and an I/O request timeout time of 60 seconds. EFS operates in two types of modes (a) Bursting mode (default mode, usually lower cost), (b) Provisioned

TABLE I: *Characteristics and I/O behavior of representative serverless applications explored in this study [44], [43], [10].*

| Application | Type | Dataset | Software Stack | I/O Request | I/O Type | Read | Write |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fully Connected (FCNN) | AI | Cifar, ImageNet | TensorFlow, Caffee | 256 KB | Sequential | 452 MB | 457 MB |
| MapReduce Sort (SORT) | Offline Analytics | Wikipedia Entries | Hadoop, Spark, Flink | 64 KB | Sequential | 43 MB | 43 MB |
| Thousand Island Scanner (THIS) | AI/Data Processing | TV News Videos | Python | 16 KB | Sequential | 5.2 MB | 1.9 MB |

throughput mode (usually higher cost). In bursting mode, except in brief burst phases, the EFS maintains a baseline throughput level as per the file system size. Note that AWS also has more storage options such as the Elastic Block Storage (EBS). However, the Lambda offering does not have direct access to the EBS solution. Moreover, unlike EFS, EBS cannot be mounted to multiple targets at a time.

How is serverless I/O different from I/O in traditional cloud computing? Serverless functions have much lesser bandwidth (only 0.5 Gb/s in AWS Lambda) than than traditional cloud VMs. Also, unlike cloud VMs, multiple serverless functions run inside one microVM (*e.g.*, Firecracker [1]) and hence the observed bandwidth by individual functions varies with time [80]. Now, we discuss our methodology.

#### III. EXPERIMENTAL METHODOLOGY

Serverless Platform. Similar to other serverless computing works, we leverage the AWS Lambda serverless platform to conduct our experiments as it is one of most commonly used serverless platforms [51], [48]. AWS Lambda offers diverse options such as multiple programming languages, memory sizes, and storage options [18], [12], [47]. AWS Lambdas run on micro VMs scheduled on AWS Elastic Compute Cloud (EC2) [80], [1], [24]. We conduct our experiments by executing different numbers of concurrent invocations (upto 1000) of Lambdas for our evaluated applications. The trends in performance remain similar for more than 1000 concurrent invocations. For invoking multiple Lambdas concurrently, we use AWS Step Functions, which support dynamic parallelism. For concurrent invocations, AWS runs identical tasks in parallel, where each task invokes a Lambda [25], [22].

Storage Options. Since serverless functions are stateless and they cannot communicate with one another, they need to access network based storages to perform I/O. Cloud offers object based storage and file systems. Lambdas have access to both the types of storage options: S3 and EFS, respectively. Both are described in the previous section [57], [85], [32]. While there is no option to tune I/O throughput on S3 [28], [39], EFS has different modes of operation [61], [41], [31]. We examine EFS in both bursting and provisioned throughput modes. In all our experiments the baseline throughput in bursting mode is 100 MB/s. In provisioned throughput mode, we vary its provisioned throughput from 150 MB/s (1.50×) to 250 MB/s (2.5×). Note that when a new EFS is created and is used in bursting mode, it has an initial burst credit of 2.1 TB, with which it can burst for a maximum of 6.12 hours. But the actual amount of time it can burst per day varies according to the EFS size [78], [69]. In our case, the EFS bursting time is 7.2 mins/day; we specifically ensure that the burst outliers do not affect our results and findings for our regular experiments where the effect of bursting behavior is not being investigated – during our experiment campaign, bursts are already consumed during preliminary warm-up runs on a given day. Note that AWS offers other database storage services like DynamoDB with Lambdas. However, due to heavy consistency requirements, databases have a strict threshold in the number of concurrent connections to it [40], [20], [49]. Hence they are not suitable for parallel invocations of serverless functions as each of the functions create a separate connection to the database. Also, they can only hold small chunks of data (< 4KB) and have a strict throughput bound, beyond which connections are dropped, leading to a complete failure of applications [20], [49]. This is not the case with S3 and EFS, where connections are only delayed due to I/O contention.

Benchmarks. We study the I/O and storage characteristics for serverless computing using the benchmarks and applications listed in Table I. These applications are widely used for serverless benchmarking [44], [43], [10] as they capture a wide range of I/O and compute characteristics, as described next. In general, serverless applications perform sequential I/O in the beginning (to load data and dependencies) and end (to write back output) of their execution as they are stateless and cannot communicate with one another [44], [43], [84]. We measured random I/O performance with FIO micro-benchmark [4] using 40MB of read/write data (similar to SORT). The obtained result characteristics are the same as sequential I/O.

Fully Connected (FCNN) is a neural network benchmark performing image classification from BigDataBench [81]. MapReduce Sort (SORT) [43] is a Hadoop implementation of a sorting algorithm. Thousand Island Scanner (THIS) [59] is a distributed video processor for serverless workers which performs video encoding and classification using MXNET DNN. The input data path was adjusted in the source code of these benchmarks to make them work for both S3 and EFS. For benchmarks which read data from a shared file (SORT and THIS), each of the serverless functions read data from a different byte location in the shared file. For FCNN, each of the serverless workers read and write to separate files. For SORT, the serverless workers write to a shared file and for THIS, they write to separate files.

Metrics of Evaluation. To perform a systematic exploration and analysis, we measured the read and write performance by instrumenting the code of our applications and accurately measuring the time taken by each I/O phase. Our instrumentation only captures the timing information and does not alter the underlying I/O characteristics of the application. We focus on the read and write I/O phase times as the primary metrics because they directly affect the overall turn around time of the

![](_page_3_Figure_0.png)

Fig. 2: *The read time of one invocation is over 2*× *lower with EFS storage as compared with S3 storage.*

application and hence, the bill paid by the end user.

We use the following metrics for performance characterization and analysis in our paper: *Read Time / Read I/O Performance.* The total time taken by the benchmark to read data from external storage. *Write Time / Write I/O Performance.* The total time taken by the benchmark to write back data to the external storage. *I/O Time.* The sum of read time and write time. *Compute Time.* Time taken by the Lambda to perform computations on the data read from storage. *Run Time.* The total execution time of a Lambda: the sum of I/O time and compute time. *Wait Time.* The time from the invocation to the start of a Lambda. *Service Time.* The total time required for an invocation to be served: the sum of wait time and run time.

To study the variability in I/O performance among concurrent invocations of Lambdas, we study the 50th (median), 95th (tail) and 100th (maximum) percentile performance of the above metrics. Fig. 1 is an overview of the workflow for our analysis. Serverless functions are implemented using similar technology (microVM, with limited bandwidth) by different cloud providers and hence the insights drawn in this paper are applicable for other providers also. At present, only AWS Lambdas have the option to access a file based storage (EFS) and hence we performed this analysis on Amazon Cloud.

#### IV. STUDYING SERVERLESS I/O BEHAVIOR

In this section, we analyze the I/O performance of three widely-used, I/O-intensive serverless applications.

### A. Read I/O Performance

First, we compare the read performance of EFS and S3 for a single application invocation (one lambda is launched).

Single Lambda read I/O performance. Fig. 2 shows the read time of one invocation for all three applications when using EFS vs. S3 as the storage engine. First, we observe that, as expected, EFS outperforms S3 consistently and significantly (>2×) for all applications. For example, for FCNN (Fig. 2(a)), the read time with EFS is less than 2 seconds, while the read time with S3 is over four seconds. This behavior is because EFS provides faster read bandwidth than S3 (the typical baseline bandwidth on EFS is 100 MB/s, while the median observed read bandwidth on S3 is 75 MB/s). Further, we verified that this observation is similar to the read performance obtained when executing a single application copy on a general-purpose M5 family Amazon EC2 instance.

Given that serverless computing model is particularly attractive for achieving concurrency, next, we investigate how

![](_page_3_Figure_11.png)

Fig. 3: *As the number of invocations are increased to* 1,000, *the median read time among the invocations remains largely similar on EFS and S3 (except for FCNN running on EFS).*

the read performance scales as we increase the number of concurrent invocations (from 100 Lambdas to 1,000 Lambdas). Studying this performance is useful to understand the trade-off in I/O performance when multiple invocations are performed concurrently. Note that all concurrently invoked Lambdas belong to the same application and perform the same I/O, but different Lambda may observe different I/O bandwidth and hence, take different time to finish the same amount and type of I/O. Because different Lambdas can observe different I/O bandwidth, we study both the median and tail behavior.

Concurrent Lambda read I/O performance. First, we report the median read performance of all concurrent invocations (i.e., the median read time among all the concurrent Lambdas). Fig. 3 shows the median read I/O times with different number of invocations using EFS and S3 as storage engines.

We make several observations. First, we note that EFS continues to outperform S3 in terms of median read performance at all concurrency levels. Second, the median read times largely remain similar for both EFS and S3 even as the degree of concurrency increases (except FCNN application, Fig. 3(a)). For the FCNN application, the median read time decreases on EFS as the number of invocations increase. This is because the average read bandwidth for EFS can increase as the number of concurrent invocations goes up for nonshared files [78]. This is because, as the number of concurrent invocations increase, the size of the file system increases, and with that the throughput scales up linearly.

Recall that each of the Lambdas in SORT and THIS appli-

![](_page_4_Figure_0.png)

Fig. 4: *When considering the tail read time, EFS performs worse than S3 for high number of invocations (80 seconds vs. 6 seconds) for FCNN. For the other applications, EFS performs better for read time.*

cations reads from a shared file, although the Lambdas access disjoint parts of the shared file. But, each of the Lambdas in FCNN reads from its own private file and observe a better average read performance. We confirmed these trends via microbenchmarks mimicking similar I/O behavior (i.e., read I/O to shared and private files across concurrent Lambdas).

Overall, EFS outperforms S3 in terms of median read performance for all benchmarks even when the concurrency is high and when private files are used for reading. An implication for programmers is that for read-intensive workloads, EFS should be the preferred choice if median read I/O performance is of importance, and private file per Lambda can potentially provide higher median performance.

*While EFS has proven to be consistently better for median read performance, next we ask if EFS remains to be a better choice when considering tail read performance*. Fig. 4 shows the tail read times for all three applications using EFS and S3. We observe that SORT and THIS continue to observe better read performance with EFS than S3. In contrast, for FCNN, the tail read time for large number of concurrent invocations is much worse with EFS than with S3. On S3, the tail read time is consistent at about 6 seconds even with 1,000 invocations. However, the tail read time starts getting worse with EFS at 400 invocations and breaches 80 seconds at 800 invocations. Somewhat surprisingly, while the median read I/O performance may improve (Fig. 3(a)), the tail read I/O performance may degrade significantly on EFS. This is due to the FCNN characteristic of reading relatively large data from separate files, which causes contention in the EFS, leading to the read I/O of some Lambdas slowing down considerably, although the average performance among all Lambdas tends to improve as shown earlier. Later, in Sec. IV-D, we present an approach to mitigate this degradation.

Lastly, we note that the worst case (100th percentile) read I/O performance among all concurrent invocations follows the same trend as the tail read I/O performance (results not shown for brevity). For example, for 1,000 concurrent Lambdas, the slowest Lambda for FCNN using EFS is significantly worse than the slowest Lambda when using S3 (over 200 seconds with EFS vs. less than 40 seconds with S3). This has an useful implication for programmers whose applications rely on all Lambdas finishing the read phase before the user can use the output for future exploration or analysis (i.e., the application is as slow as the slowest Lambda). In some cases, non-uniform input read I/O performance can cause non-synchronous start of the compute phase which may be undesirable or inefficient.

*On I/O from EC2 instances.* To investigate further how serverless Lambda I/O characteristics are different from traditional VMs (EC2 in Amazon) , we spawned multiple copies of the same application on docker containers inside one generalpurpose EC2 instance (M5 family). Recall that EC2 instances are not suitable for the use-case of serverless applications and require much longer provisioning time and undesirable increase in cost at a high concurrency level. Therefore, such a comparison is unfair. Nevertheless, we learned two important lessons. First, spawning concurrent functions natively on EC2 instances suffers from severe on-node resource contention, making the compute time and compute time variability worse – significantly worse than the Lambda experiments. AWS manages Lambda running microVMs in a different way to avoid such issues.

Second, functions invoked inside an EC2 instance become mostly network-bandwidth bound as their containers share the overall network-bandwidth with each other in an uncoordinated fashion, while each Lambda invocation gets 0.5Gb/s network bandwidth. Consequently, I/O from Lambda invocations, esp. at a high concurrency level, deserves more research attention as they expose new performance issues.

Summary and Implication. For read-intensive workloads, EFS should be the preferred choice over S3, if the median read I/O performance is a major figure of merit and the degree of concurrency is low. At high concurrency, the choice of a better storage engine becomes complex and application-dependent. In contrast to median read performance choice, S3 may be a better choice compared to EFS in some cases if tail read I/O performance is the primary performance metric. Previous studies have shown that serverless I/O is of concern only for small-sized (< 100KB) files [43], [63], our experiments reveal that serverless I/O is a performance bottleneck even for applications with sequential I/O pattern reading large files at high concurrency – this

78

![](_page_5_Figure_0.png)

Fig. 5: *With one invocation, the write time can be better on either storage systems depending on the application.*

opens the opportunity for new mitigation strategies.

#### B. Write I/O Performance

We now investigate the write I/O performance using a single and multiple concurrent Lambda invocations.

Single Lambda write I/O performance. Fig. 5 shows the time taken to complete the write phase when only one Lambda is invoked. Surprisingly, unlike the read I/O performance trends, EFS is not the clear winner over S3.

For FCNN (Fig. 5(a)), the write I/O performance with EFS is better than S3, similar to the read I/O performance trend where EFS outperformed S3. However, for SORT application (Fig. 5(b)), the write time with EFS is much slower than the write time with S3 (2.6 seconds vs. 1.7 seconds, 1.5× worse). Recall that for the same application (SORT), EFS read I/O performance for SORT was over 4× better than S3 (Fig. 2). The reversed trend in write I/O for SORT is because of the considerable worsening of its write time on EFS.

In fact, we observe that on EFS, the write I/O performance is much worse than the read I/O performance for all applications even though when they perform equal or lesser amount of write I/O than read I/O (Fig. 2 vs. Fig. 5). In contrast, when using S3 the observed read and write bandwidths are similar. For example, with FCNN, it takes ≈1.8 seconds to read 450 MB of data from EFS, but it takes ≈3.2 seconds to write the same data back to EFS (more than 1.7× slower), while S3 provides roughly similar performance. This is because EFS maintains a strong consistency model, replicating data for backup concurrently during write phase across multiple geodistributed servers, thus affecting the write performance [78]. Whereas, S3 maintains an eventual consistency model, which gradually replicates data across servers, not concurrently but after the completion of the write phase [19], [3].

Concurrent Lambda write I/O performance. First, we analyze the median write performance and then, the tail write I/O performance. Fig. 6 shows the median write times with different number of invocations on EFS and S3 for all three applications. We make several interesting observations.

Recall that as the number of concurrent invocations increased, the median read time performance remained similar when using both the EFS and S3 storage engines (Fig. 3). Interestingly, the same trend does not hold true for EFS. As the number of concurrent invocations increase, the median write performance for EFS degrades almost linearly with the number of invocations. This trend is observed for all three applications, although they perform different amount of total

![](_page_5_Figure_10.png)

Fig. 6: *As the number of concurrent invocations increase to* 1,000*, the median write time remains consistent on S3. On EFS, it increases linearly with the number of invocations.*

I/O and their per request I/O size also varies. However, with S3 storage engine, the same applications do not exhibit such a trend – the write I/O performance remains roughly similar across different number of Lambdas.

Scaling up the number of Lambdas further exacerbates the performance gap between EFS and S3. At 1,000 concurrent Lambdas, the EFS write performance is almost two orders of magnitude worse than the S3 write performance. For example, with SORT (Fig. 6(b)), the median write time is almost 300 seconds on EFS for 1,000 concurrent invocations, but the median write time is 1.4 seconds on S3 across all number of concurrent invocations. Even at lower concurrent Lambda count (e.g., 100), the EFS write performance is almost 10× worse than S3.

Recall that for SORT, the concurrent Lambdas write to the same file, while in FCNN, each Lambda write to a different file. But, both the applications observe this trend. This indicates that the writes originating from Lambdas are being treated fundamentally different on EFS and S3. On S3, even when 1,000 concurrent invocations are writing to the same bucket, the writes do not observe a significant degradation compared to one invocation. This is because of several reasons.

Firstly, different files are treated as separate objects when using S3 engine, hence there is no contention caused by different Lambdas trying to write to a bucket concurrently. They can all write in parallel. On the other hand, EFS has strict consistency model checks that contribute to the writes from concurrent invocations being sequentialized [72], [56]. When different Lambdas attempt to write to the same file, as

![](_page_6_Figure_0.png)

Fig. 7: *EFS has worse tail write times than S3 for a large number of invocations. With EFS, the tail write times increase linearly with number of invocations. With S3, they do not.*

in SORT, due to the consistency model of EFS, each Lambda puts a lock the file during its write phase preventing others to write to it [77], [19]. This further increases the write time.

Conversely, there is no concept of I/O throughput limitation on S3. The achieved throughput from S3 is primarily determined by the bandwidth of the VM where a Lambda is running. In contrast, EFS has a throughput bound on the storage side, which degrades performance when multiple Lambdas try to write concurrently. For SORT, the degradation of write performance in EFS is due to two reasons: (1) write serialization in EFS as output is being written in a shared file by different concurrent Lambdas. (2) throughput bound of EFS degrades performance as the number of concurrent invocations increase. For FCNN and THIS, the performance degradation is only due to the second reason as the benchmarks write to different files.

Next, we study the tail write I/O performance as we increase the number of concurrent Lambdas. Fig. 7 shows the tail write times with different number of invocations with EFS and S3 for all three applications. Similar to the median write I/O performance, as the number of concurrent invocations are increased when using EFS, the tail write times increase almost linearly across all three applications. In contrast, the tail write I/O performance among the invocations remains largely similar on S3. For example, with FCNN (Fig. 7(a)), the tail write time is over 600 seconds on EFS for 1,000 concurrent invocations, but the tail write time is ≈6.2 seconds on S3 across all number of concurrent invocations. We also note that the trends of maximum write times of concurrent invocations remain similar to tail write times (the results are not plotted for brevity).

These results demonstrate that when multiple invocations perform writes concurrently, S3 is a better choice across all QoS requirements (median, tail, and maximum). Note that, at a large number of concurrent invocations, the cost with S3 is much lower than EFS, even though the overall performance on EFS is worse than S3 due to the much increased write time.

*On I/O from EC2 instances.* To investigate the write performance issues further, we spawned multiple copies of the same application on a EC2 instance (M5 family). Recall that such a comparison is unfair as discussed earlier. Our experiments revealed that (1) EFS appears to perform better than S3 as expected. and (2) functions invoked inside an EC2 instance do not observe severe write I/O performance degradation with EFS even as the concurrency grows – unlike our Lambda experiments. The reason is hidden under how AWS manages Lambda instances. AWS instantiates multiple new connections to EFS for write from each of the Lambda invocations, while all writers from the same EC2 instance are a part of a single connection. Multiple connections lead to more overhead due to context switching delay among them and consistency checks of EFS after each connection has performed I/O.

Summary and Implication. In contrast to previous works [43], [44], [63] which did not identify performance issues between read and write performance of serverless applications, we discover that read and write performance trends are significantly different esp. at high concurrency levels. Unlike the read I/O performance, EFS generally does not always outperform S3 for write I/O performance. Unfortunately, EFS performance gets worse with high concurrency. The median write times, tail write times, and worst-case write I/O performance increases linearly with the number of invocations on EFS. On the other hand, S3 write times do not degrade with more concurrent invocations due to differences in consistency model of an object storage and a traditional file system. Serverless applications that rely on the concurrent invocations to synchronize at the end of the write phase could suffer from inefficiency, especially at higher degrees of concurrency.

## C. Effect of Increased Throughput and Capacity Provisioning on EFS Performance

Recall that when EFS is runs in default mode, it is bounded by the baseline throughput which is determined by the amount of data stored under the file system. In all our experiments, this baseline throughput is 100 MB/s. While EFS has the ability to burst, the bursting time quota per day (7.2 minutes/day) prevents it from bursting even when it has bursting credits. We investigate whether the EFS I/O performance challenges for serverless applications can be mitigated by buying additional I/O throughput (this option is not applicable to S3 though).

(1) Increased Throughput. Recall that EFS can also be used in provisioned throughput mode where a constant throughput level is guaranteed from the storage system. If we provision

![](_page_7_Figure_0.png)

1.5× 2× 2.5× Fig. 8: *Provisioning additional throughput and capacity pro-*

*vides limited improvement in read I/O performance, which diminishes as the invocation concurrency increases.*

higher throughput for EFS than our baseline throughput of 100 MB/s, one might expect to see improvement in I/O performance as increasing the throughput amounts to increasing transfer bandwidth from the EFS side. We experimented with increasing throughput by provisioning EFS in the range of 150 MB/s (1.50×) to 250 MB/s (2.5×).

(2) Increased Capacity. When using EFS in default (bursting) mode, the baseline throughput scales proportionately with the amount of data contained in EFS. One way to improve the baseline performance of EFS would be to add dummy data to EFS to improve the baseline I/O performance. In our experiments, we artificially increased our EFS size to increase the baseline throughput of EFS in the range of 150 MB/s to 250 MB/s. While, this method should deliver similar performance as the provisioned throughput method, it is worth exploring as it has a different pricing model.

Fig. 8 shows the read I/O performance for all three applications under different levels of increase in throughput and capacity. Similarly, Fig. 9 shows the write I/O performance under different levels of increase in throughput and capacity. Both results also capture the observed trend in change of I/O performance as the degree of concurrency is increased from 1 to 1,000. These results reveal various interesting patterns.

First, neither increased provisioned throughput nor increased capacity helps us to consistently improve the I/O performance across all applications. In fact, contrary to our expectation increasing the throughput via these methods, as a first-guess remedy, may degrade the I/O performance, at some higher concurrency levels. Some applications (e.g., FCNN and SORT) tend to observe significant improvement at lower concurrency levels, but these improvements evaporate at higher concurrency. Similar unexpected behavior was repeated

![](_page_7_Figure_7.png)

Fig. 9: *Provisioning additional throughput and capacity provides limited improvement in write I/O performance, which diminishes as the invocation concurrency increases.*

and confirmed through micro-benchmarking with controlled Lambda invocations.

The main reason for this degradation and counter-intuitive trend is that the EFS servers may get overly congested and overloaded. When the EFS bandwidth is increased, write I/O requests (network packets) from concurrent invocations arrive at the EFS at a faster rate, overwhelming the servers. In this process, many of the queued incoming packets may get potentially dropped due to the high volume. These packets have to be reissued by the NFS clients mounted on the Lambda, thus, increasing the write I/O time [8], [5]. In fact, the temporary backlog on the server side can also slow down transmissions on the client side [8], [5].

Note that, using 2× provisioned throughput, the cost of running Lambdas increases by 11% on an average for 1,000 concurrent invocations. Also, increasing capacity and increasing throughput has similar effect in terms of cost, with increasing throughput costing ≈4% more than increasing capacity.

Summary and Implication. Increasing provisioned throughput and capacity offers limited improvement in observed I/O performance of Lambdas. Non-intuitive trend may be encountered in some cases where the I/O performance suffers compared to baseline (bursting mode), at higher concurrency level. Furthermore, both of these approaches might not be cost-effective and make the EFS option more expensive than S3. Thus, end-users should exercise increasing provisioned throughput and capacity carefully as it may not always bring the desired level of performance improvement at high concurrency level.

## D. Mitigating I/O Performance Issues for a Large Number of Concurrent Lambdas

The major lesson learned from the previous experiments is that provisioning higher throughput or increasing the capacity of the EFS may not always improve the I/O performance, especially when the end user is using Lambdas with high concurrency. If we can improve its I/O performance, EFS can still be useful for serverless applications that require customizable file system features such as a directory structure and security/permissions features. But, the performance issues cannot be simply mitigated by provisioning for higher bandwidth. Instead it could be improved if the I/O contention is managed carefully and I/O activity is coordinated intelligently. Unfortunately, this is a non-trivial challenge since Lambdas cannot communicate directly with each other to coordinate their I/O, and even if they were, they would need to perform communication I/O in order to schedule their primary I/O, which would further aggravate the problem. To address this challenge, we experimented with a relatively simple, but effective, approach to mitigate this challenge: *Stagger the Lambdas*.

The key idea is to divide the Lambda invocations into batches - where the size of the batch (number of Lambdas invoked together) and delay between two batch invocations can be controlled. This approach does not require any changes/ instrumentation to the application, and does not change the expected behavior of the application. The Lambdas in a batch are scheduled together and each batch is scheduled after a set delay from the previous batch. For example, if 1,000 invocations are to be scheduled with batch size of 50 and delay time of two seconds, then the first 50 invocations are scheduled at the 0th second, the next 50 are scheduled at the 2 nd second, and the last 50 are scheduled at the 38th second.

The expected trade-off is that the I/O performance is likely to improve due to lesser contention, but the wait time increases due to artificially injected delays. Next, we present results to quantify these trade-offs when 1,000 Lambdas are concurrently executed with staggered delays. Note that we present results as % improvement over the baseline (all 1,000 invocations launched together) instead of absolute values since different components of the service time have different scope of improvements and the relative improvement is more relevant in this case. Improvements are denoted in a light-colored grid box and degradations are denoted as dark grid blocks.

As expected, Fig. 10 confirms the improvement in the median write time over the baseline for different combinations of batch sizes and delay times. All three applications observe over 90% improvement in the median write time, especially for smaller batch sizes, as a result of the reduced contention in EFS. Although we observed similar improvements in the read I/O performance, we primarily analyze the write I/O performance because the write I/O performance particularly suffered from the increased Lambda concurrency (Fig. 6). However, recall that the tail read I/O performance also suffers at higher concurrency (Fig. 4, esp. for FCNN). Our results

![](_page_8_Figure_5.png)

Fig. 10: *Staggered smaller batches and larger delays result in better write I/O performance due to reduced contention.*

![](_page_8_Figure_7.png)

Fig. 11: *Staggering can improve tail read performance, especially for FCNN (compare to Fig. 3). Large degradation over the baseline (more than -500%) is approximated to -500%.*

confirm that staggered approach is effective at improving the tail read I/O performance at high Lambda concurrency (Fig. 11). As expected, we observed similar improvements in the tail write I/O performance for all three applications.

Next, we discuss the impact of the staggering approach on the wait time. As expected, staggering the Lambda invocations increases the median wait time universally for all three applications for all delay settings (Fig. 12). Applications can see a degradation of almost 500% in the median wait time of the 1,000 invocations, especially when the batch size is 10 and the delay time is 2.5 second (last batch gets scheduled at the ((1000/10) − 1) × 2.5 = 247.5 th sec. as opposed to all invocations getting launched at the 0 th sec).

However, the increase in wait time can be compensated by the improvement in the I/O time (staggering does not directly affect the compute performance). Fig. 13 indicates that staggering considerably improves the median service time for relatively high-I/O-size applications like FCNN and SORT (over 80% improvement), due to the improvement in the median write time in spite of the large increase in the median wait time. Here, the service time refers to the time from the submission of the first batch to the completion of individual invocations. Due to its small write size, THIS is unable to observe any improvement from staggering.

Encouraged by the effectiveness of the staggering approach, we applied the same technique when Lambdas use S3. We obtained similar performance trends, with lesser I/O improvement than EFS because S3 does not suffer from severe write I/O degradation at increased concurrency (Fig. 6). Interestingly, we discovered that the staggering appears to help in unexpected ways when used with S3. When 1,000 Lambdas are launched concurrently with S3, some Lambdas observe

![](_page_9_Figure_0.png)

Fig. 12: *As expected, staggered Lambdas can considerably increase the median wait times for all applications.*

![](_page_9_Figure_2.png)

Fig. 13: *Staggering can strike a balance between write performance improvement and wait time degradation to improve the overall service time by up to 85% over the baseline.*

increased long wait times before they are started (unlike EFS). Batching the Lambdas in smaller sizes reduces such long wait time delays. Staggering exposes an interesting nuance of how Lambda scheduling works with different storage engines. We note that the optimal value of delay and batch size is dependent on application characteristics – while an ad-hoc value may provide improvement, achieving optimality may indeed require more effort.

Summary and Implication. (1) Staggering can improve the *overall service time* of Lambdas with EFS at higher degree of concurrency, and does not require high level of parameter tuning for observing significant improvement. However, careful tuning could produce higher performance improvement. (2) Staggering needs to be carefully applied for applications with relatively low I/O intensity (e.g., THIS) since the wait time increase may not always compensate the decrease in the I/O time and hence, the decrease in the overall service time might be limited. This opens the opportunity to optimally determine the value of delay and batch size for a given application and concurrency level.

## V. DISCUSSION

Addressing Slow Write I/O Performance via One File Per Directory. Each invocation of FCNN creates and writes to individual files within a single directory on EFS. To improve the write I/O performance at a high concurrency, we examined an alternative directory structure where each file is created under a separate directory, but it did not affect our findings.

Creating a New Instance of Elastic File System for Each Run. We hypothesized that sharing a file system among runs could create undesired side-effects as burst credits might get used up by the time later runs are executed (recall we run ten runs for each type of experiment). Therefore, we experimented with another potential remedy: creating and mounting new EFS for each run. Note that this fix is rather impractical since it is not feasible to create a large number of EFS instances and mount them on the fly – it poses both high overhead toward total service time and may require copying data frequently.

We specifically attempted this fix to understand its impact on write I/O performance with high number of invocations. We found that, although this approach cannot be frequently applied in practice, the median read and write I/O performances are indeed improved by ≈70% for both, one and 1,000 concurrent invocations. This results suggest that the internals of EFS implementation under high concurrent write load is potentially responsible for this behavior (e.g., the protocol for ensuring consistency across multiple invocations and geo-distributed replicas). For S3, since each file is treated as a separate object, initializing a new S3 bucket for each invocation makes no difference. In fact, the concept of bucket is there to simply serve the purpose of organizing files.

Impact on Compute Time and Effect of Varying Memory Size of the Lambda Invocation. The choice of storage engine do not impact the compute time trends, and our findings are not sensitive to the allocated memory size of the Lambda function.

#### VI. RELATED WORK

Cloud computing vendors have a multitude of storage and compute options to choose from [13], [29], [82]. However, since the access and invocation pattern of these workloads may change with time, the allocated resources should also have the capability to scale accordingly. This has led to the development of various predictive [16], [45], and hybrid [35] approaches focusing on on-demand cloud resource scaling. While some of the works deal with rightsizing jobs at the granularity of traditional VMs [33], [2], other works deal with determining fine grained storage requirements for cloud applications [53], [52]. Next, for applications running on cloud VMs, performance variability is a major issue [67], [15], [62], [75], [34]. Previous works have dedicated some effort toward characterizing this variability: the variability arises as most of the cloud services run on shared physical hardware [66], [14]. Performance can vary depending upon the choice and type of compute and storage resources [74], [34]. All of these works are based on IaaS (Infrastructure as a Service) type of cloud environments where applications are run on shared VMs, which are managed and configured by the user. I/O congestion has also been studied in the context of HPC systems [70], [27], [11], [86], [17], [6], [21], [7], [27], [83]. However, due to statelessness and limited bandwidth, serverless platforms are fundamentally different from on-premise clusters and hence the developed strategies cannot be adopted.

The I/O problem is aggravated for serverless functions as they are allowed little ephemeral storage and require frequent read/write accesses to external storage [55], [50], [76], [58], [44], [43]. Some works have also contributed toward making application-specific choices of serverless ephemeral storage, exploiting serverless temporary storage for caching [44], [42], [79]. But, unlike our work, these previous works have not provided a detailed characterization of storage performance issues of read and write I/O for different representative applications run using different serverless storage options. In contrast to recent works [79], [11], [68], [43], [44], [63], [26], [84], our study reveals multiple new interesting and alarming trends (including the I/O bottleneck is particularly severe at a high concurrency level, how storage engine choice (EFS vs. S3) may affect the performance) and a new non-intrusive technique to mitigate the I/O performance issues.

#### VII. CONCLUSION

To the best of our knowledge, we present the first detailed analysis of serverless I/O and storage characteristics and solutions to optimize for serverless I/O performance of EFS. Our analysis captures the complex interaction between serverless functions and storage devices. To help advance research in serverless I/O, our artifact is available at: https://zenodo.org/record/5539888

#### ACKNOWLEDGEMENT

We thank anonymous reviewers for their constructive feedback. We are grateful to first-line responders and essential workers who have worked tirelessly to keep our community safe and functioning during the COVID-19 pandemic, and hence, enabled us to devote time to performing this research work. We acknowledge support from NSF awards 2124897 and 1910601, MGHPCC, and Northeastern University.

#### REFERENCES

- [1] A. Agache, M. Brooker, A. Iordache, A. Liguori, R. Neugebauer, P. Piwonka, and D.-M. Popa. Firecracker: Lightweight virtualization for serverless applications. In *17th* {*USENIX*} *Symposium on Networked Systems Design and Implementation (*{NSDI} 20), pages 419–434, 2020.
- [2] O. Alipourfard, H. H. Liu, J. Chen, S. Venkataraman, M. Yu, and M. Zhang. Cherrypick: Adaptively unearthing the best cloud configurations for big data analytics. In *14th* {*USENIX*} *Symposium on Networked Systems Design and Implementation (*{*NSDI*} 17), pages 469–482, 2017.
- [3] E. Amazon. Amazon web services. *Available in: http://aws. amazon. com/es/ec2/(November 2012)*, 2015.
- [4] J. Axboe. Fio-flexible i/o tester synthetic benchmark. *URL https://github. com/axboe/fio (Accessed: 2015-06-13)*, 2005.
- [5] A. Batsakis, R. Burns, A. Kanevsky, J. Lentini, and T. Talpey. Ca-nfs: A congestion-aware network file system. *ACM Transactions on Storage (TOS)*, 5(4):1–24, 2009.
- [6] M. Bauer and M. Garland. Legate numpy: Accelerated and distributed array computing. In *2019 Proc. of the International Conference for High Performance Computing, Networking, Storage and Analysis*.
- [7] B. Behzad, S. Byna, and M. Snir. Optimizing i/o performance of hpc applications with autotuning. *ACM Transactions on Parallel Computing (TOPC)*, 5(4):1–27, 2019.
- [8] J. M. Bennett, M. A. Bauer, and D. Kinchlea. Characteristics of files in nfs environments. *ACM SIGSMALL/PC Notes*, 18(3-4):18–25, 1992.
- [9] J. Beswick. Using amazon efs for aws lambda in your serverless applications, Jun 2020.

- [10] S. Bitchebe, D. Mvondo, A. Tchana, L. Reveill ´ ere, and N. De Palma. ` Intel page modification logging, a hardware virtualization feature: study and improvement for virtual machine working set estimation. *arXiv preprint arXiv:2001.09991*, 2020.
- [11] B. Carver, J. Zhang, A. Wang, A. Anwar, P. Wu, and Y. Cheng. Wukong: a scalable and locality-enhanced framework for serverless parallel computing. In *Proceedings of the 11th ACM Symposium on Cloud Computing*, pages 1–15, 2020.
- [12] P. Castro, V. Ishakian, V. Muthusamy, and A. Slominski. Serverless programming (function as a service). In *2017 IEEE 37th International Conference on Distributed Computing Systems (ICDCS)*, pages 2658– 2659. IEEE, 2017.
- [13] S. Chaisiri, R. Kaewpuang, B.-S. Lee, and D. Niyato. Cost minimization for provisioning virtual servers in amazon elastic compute cloud. In *2011 IEEE 19th Annual International Symposium on Modelling, Analysis, and Simulation of Computer and Telecommunication Systems*.
- [14] L. Chen, H. Shen, and S. Platt. Cache contention aware virtual machine placement and migration in cloud datacenters. In *2016 IEEE 24th International Conference on Network Protocols (ICNP)*.
- [15] Y. Chen, A. S. Ganapathi, R. Griffith, and R. H. Katz. Towards understanding cloud performance tradeoffs using statistical workload analysis and replay. *University of California at Berkeley, Technical Report No. UCB/EECS-2010-81*, 2010.
- [16] E. Cortez, A. Bonde, A. Muzio, M. Russinovich, M. Fontoura, and R. Bianchini. Resource central: Understanding and predicting workloads for improved resource management in large cloud platforms. In *Proceedings of the 26th Symposium on Operating Systems Principles*, pages 153–167, 2017.
- [17] R. Crespo-Cepeda, G. Agapito, J. L. Vazquez-Poletti, and M. Cannataro. Challenges and opportunities of amazon serverless lambda services in bioinformatics. In *Proceedings of the 10th ACM International Conference on Bioinformatics, Computational Biology and Health Informatics*, pages 663–668, 2019.
- [18] A. Das, S. Patterson, and M. Wittie. Edgebench: Benchmarking edge computing platforms. In *2018 IEEE/ACM International Conference on Utility and Cloud Computing Companion (UCC Companion)*, pages 175–180. IEEE, 2018.
- [19] B. David. Aws: Amazon web services tutorial for beginners. 2018.
- [20] T. Deshpande. *DynamoDB Cookbook*. Packt Publishing Ltd, 2015.
- [21] M. Dorier, G. Antoniu, R. Ross, D. Kimpe, and S. Ibrahim. Calciom: Mitigating i/o interference in hpc systems through cross-application coordination. In *2014 IEEE 28th International Parallel and Distributed Processing Symposium*, pages 155–164. IEEE, 2014.
- [22] R. Feyzkhanov. *Hands-On Serverless Deep Learning with TensorFlow and AWS Lambda: Training serverless deep learning models using the AWS infrastructure*. 2019.
- [23] K. Figiela, A. Gajek, A. Zima, B. Obrok, and M. Malawski. Performance evaluation of heterogeneous cloud functions. *Concurrency and Computation: Practice and Experience*, 30(23):e4792, 2018.
- [24] S. Fouladi, F. Romero, D. Iter, Q. Li, S. Chatterjee, C. Kozyrakis, M. Zaharia, and K. Winstein. From laptop to lambda: Outsourcing everyday jobs to thousands of transient functional containers. In *2019* {*USENIX*} *Annual Technical Conference (*{*USENIX*}{ATC} 19).
- [25] G. C. Fox, V. Ishakian, V. Muthusamy, and A. Slominski. Status of serverless computing and function-as-a-service (faas) in industry and research. *arXiv preprint arXiv:1708.08028*, 2017.
- [26] A. Fuerst and P. Sharma. Faascache: Keeping serverless computing alive with greedy-dual caching. In *ASPLOS*. ACM, 2021.
- [27] A. Gainaru, G. Aupy, A. Benoit, F. Cappello, Y. Robert, and M. Snir. Scheduling the i/o of hpc applications under congestion. In *2015 IEEE International Parallel and Distributed Processing Symposium*, pages 1013–1022. IEEE, 2015.
- [28] S. Garfinkel. An evaluation of amazon's grid computing services: Ec2, s3, and sqs. 2007.
- [29] D. Gmach, J. Rolia, and L. Cherkasova. Resource and virtualization costs up in the cloud: Models and design choices. In *IEEE/IFIP Intntl. Conference on Dependable Systems & Networks (DSN)*, pages 395–402. IEEE, 2011.
- [30] Z. Gong, X. Gu, and J. Wilkes. Press: Predictive elastic resource scaling for cloud systems. In *2010 International Conference on Network and Service Management*, pages 9–16. Ieee, 2010.
- [31] S. Gulabani. *Amazon Web Services Bootcamp: Develop a scalable, reliable, and highly available cloud environment with AWS*. 2018.

- [32] J. M. Hellerstein, J. Faleiro, J. E. Gonzalez, J. Schleier-Smith, V. Sreekanti, A. Tumanov, and C. Wu. Serverless computing: One step forward, two steps back. *arXiv preprint arXiv:1812.03651*, 2018.
- [33] H. Herodotou, F. Dong, and S. Babu. No one (cluster) size fits all: automatic cluster sizing for data-intensive analytics. In *Proceedings of the 2nd ACM Symposium on Cloud Computing*, pages 1–14, 2011.
- [34] A. Iosup, N. Yigitbasi, and D. Epema. On the performance variability of production cloud services. In *2011 11th IEEE/ACM International Symposium on Cluster, Cloud and Grid Computing*, pages 104–113. IEEE, 2011.
- [35] D. Jacobson, D. Yuan, and N. Joshi. Scryer: Netflix's predictive auto scaling engine. *Netflix Technology Blog*, 2013.
- [36] P. Jamshidi, C. Pahl, and N. C. Mendonc¸a. Pattern-based multi-cloud architecture migration. *Software: Practice and Experience*, 47(9):1159– 1184, 2017.
- [37] J. Jiang, J. Lu, G. Zhang, and G. Long. Optimal cloud resource autoscaling for web applications. In *2013 13th IEEE/ACM International Symposium on Cluster, Cloud, and Grid Computing*.
- [38] E. Jonas, J. Schleier-Smith, V. Sreekanti, C.-C. Tsai, A. Khandelwal, Q. Pu, V. Shankar, J. Carreira, K. Krauth, N. Yadwadkar, et al. Cloud programming simplified: A berkeley view on serverless computing. *arXiv preprint arXiv:1902.03383*, 2019.
- [39] M. Jung, S. Mollering, P. Dalbhanjan, P. Chapman, and C. Kassen. ¨ Microservices on aws. *Amazon Web Services, NY, USA*, 2016.
- [40] S. Kalid, A. Syed, A. Mohammad, and M. N. Halgamuge. Big-data nosql databases: A comparison and analysis of "big-table","dynamodb", and "cassandra". In *2017 IEEE 2nd International Conference on Big Data Analysis (ICBDA)*, pages 89–93. IEEE, 2017.
- [41] A. KARAWASH. Cloud storage with aws: Efs vs ebs vs s3.
- [42] A. Khandelwal, A. Kejariwal, and K. Ramasamy. Le taureau: Deconstructing the serverless landscape & a look forward. In *Proceedings of the 2020 ACM SIGMOD International Conference on Management of Data*, pages 2641–2650, 2020.
- [43] A. Klimovic, Y. Wang, C. Kozyrakis, P. Stuedi, J. Pfefferle, and A. Trivedi. Understanding ephemeral storage for serverless analytics. In *2018 USENIX Annual Technical Conference*, pages 789–794, 2018.
- [44] A. Klimovic, Y. Wang, P. Stuedi, A. Trivedi, J. Pfefferle, and C. Kozyrakis. Pocket: Elastic ephemeral storage for serverless analytics. In *13th* {*USENIX*} *Symposium on Operating Systems Design and Implementation (*{*OSDI*} 18), pages 427–444, 2018.
- [45] A. Krioukov, P. Mohan, S. Alspaugh, L. Keys, D. Culler, and R. H. Katz. Napsac: Design and implementation of a power-proportional web cluster. In *Proceedings of the first ACM SIGCOMM workshop on Green networking*, pages 15–22, 2010.
- [46] J. Kuhlenkamp, S. Werner, M. C. Borges, K. El Tal, and S. Tai. An evaluation of faas platforms as a foundation for serverless big data processing. In *Proceedings of the 12th IEEE/ACM International Conference on Utility and Cloud Computing*, pages 1–9, 2019.
- [47] D. Kumanov, L.-H. Hung, W. Lloyd, and K. Y. Yeung. Serverless computing provides on-demand high performance computing for biomedical research. *arXiv preprint arXiv:1807.11659*, 2018.
- [48] H. Lee, K. Satyam, and G. Fox. Evaluation of production serverless computing environments. In *2018 IEEE 11th International Conference on Cloud Computing (CLOUD)*, pages 442–450. IEEE, 2018.
- [49] W.-T. Lin, C. Krintz, R. Wolski, M. Zhang, X. Cai, T. Li, and W. Xu. Tracking causal order in aws lambda applications. In *2018 IEEE International Conference on Cloud Engineering (IC2E)*.
- [50] W. Lloyd, S. Ramesh, S. Chinthalapati, L. Ly, and S. Pallickara. Serverless computing: An investigation of factors influencing microservice performance. In *2018 IEEE Intntl. Conf. on Cloud Engineering (IC2E)*.
- [51] T. Lynn, P. Rosati, A. Lejeune, and V. Emeakaroha. A preliminary review of enterprise serverless cloud computing (function-as-a-service) platforms. In *2017 IEEE International Conference on Cloud Computing Technology and Science (CloudCom)*, pages 162–169. IEEE, 2017.
- [52] A. Mahgoub, A. M. Medoff, R. Kumar, S. Mitra, A. Klimovic, S. Chaterji, and S. Bagchi. {OPTIMUSCLOUD}: Heterogeneous configuration optimization for distributed databases in the cloud. In *2020 USENIX Annual Technical Conference*, pages 189–203, 2020.
- [53] A. Mahgoub, P. Wood, A. Medoff, S. Mitra, F. Meyer, S. Chaterji, and S. Bagchi. {SOPHIA}: Online reconfiguration of clustered nosql databases for time-varying workloads. In *2019 USENIX Annual Technical Conference*, pages 223–240, 2019.

- [54] M. Malawski, K. Figiela, A. Gajek, and A. Zima. Benchmarking heterogeneous cloud functions. In *European Conference on Parallel Processing*, 2017.
- [55] G. McGrath and P. R. Brenner. Serverless computing: Design, implementation, and performance. In *2017 IEEE 37th International Conference on Distributed Computing Systems Workshops (ICDCSW)*, pages 405–410. IEEE, 2017.
- [56] C. D. OPARA. Cloud computing in amazon web services, microsoft windows azure, google app engine and ibm cloud platforms: A comparative study.
- [57] I. Pelle, J. Czentye, J. Doka, and B. Sonkoly. Towards latency sensitive ´ cloud native applications: A performance study on aws. In *2019 IEEE 12th International Conference on Cloud Computing (CLOUD)*, pages 272–280. IEEE, 2019.
- [58] Q. Pu, S. Venkataraman, and I. Stoica. Shuffling, fast and slow: Scalable analytics on serverless infrastructure. In *16th* {*USENIX*} *Symposium on Networked Systems Design and Implementation (*{*NSDI*} 19).
- [59] J. H. Qian Li and D. D. Thousand island scanner: Scaling video analysis on aws lambda., 2018.
- [60] J. Sampe, G. Vernik, M. S ´ anchez-Artigas, and P. Garc ´ ´ıa-Lopez. Server- ´ less data analytics in the ibm cloud. In *Proceedings of the 19th International Middleware Conference Industry*, pages 1–8, 2018.
- [61] H. Saxena and J. Pound. A cloud-native architecture for replicated data services. In *12th* {*USENIX*} *Workshop on Hot Topics in Cloud Computing (HotCloud 20)*, 2020.
- [62] J. Schad, J. Dittrich, and J.-A. Quiane-Ruiz. Runtime measurements in ´ the cloud: observing, analyzing, and reducing variance. *Proceedings of the VLDB Endowment*, 3(1-2):460–471, 2010.
- [63] J. Schleier-Smith, L. Holz, N. Pemberton, and J. M. Hellerstein. A faas file system for serverless computing.
- [64] V. Shankar, K. Krauth, Q. Pu, E. Jonas, S. Venkataraman, I. Stoica, B. Recht, and J. Ragan-Kelley. Numpywren: Serverless linear algebra. *arXiv preprint arXiv:1810.09679*, 2018.
- [65] Z. Shen, S. Subbiah, X. Gu, and J. Wilkes. Cloudscale: elastic resource scaling for multi-tenant cloud systems. In *Proceedings of the 2nd ACM Symposium on Cloud Computing*, pages 1–14, 2011.
- [66] J.-Y. Shin, M. Balakrishnan, L. Ganesh, T. Marian, and H. Weatherspoon. Gecko: A contention-oblivious design for cloud storage. In *HotStorage*, 2012.
- [67] L. Suresh, M. Canini, S. Schmid, and A. Feldmann. C3: Cutting tail latency in cloud data stores via adaptive replica selection. In *2015 USENIX Symposium on Networked Systems Design and Implementation*.
- [68] D. Taibi, N. El Ioini, C. Pahl, and J. R. S. Niederkofler. Serverless cloud computing (function-as-a-service) patterns: A multivocal literature review. In *Proceedings of the 10th International Conference on Cloud Computing and Services Science (CLOSER'20)*, 2020.
- [69] V. Tankariya and B. Parmar. *AWS Certified Developer-Associate Guide: Your one-stop solution to pass the AWS developer's certification*. 2017.
- [70] M. Taufer. Who is afraid of i/o?: Exploring i/o challenges and opportunities at the exascale. In *ScienceCloud at HPDC*, page 1, 2016.
- [71] D. Team. *Aws Lambda Developer Guide*. Samurai Media Limited, London, GBR, 2018.
- [72] L. Teylo, R. C. Brum, L. Arantes, P. Sens, and L. M. d. A. Drummond. Developing checkpointing and recovery procedures with the storage services of amazon web services. In *49th International Conference on Parallel Processing-ICPP: Workshops*, pages 1–8, 2020.
- [73] B. Trushkowsky, P. Bod´ık, A. Fox, M. J. Franklin, M. I. Jordan, and D. A. Patterson. The scads director: Scaling a distributed storage system under stringent performance requirements. In *FAST*, volume 11, pages 163–176, 2011.
- [74] R. Tudoran, A. Costan, G. Antoniu, and L. Bouge. A performance ´ evaluation of azure and nimbus clouds for scientific applications. In *Proc. of the 2012 Intntl. Workshop on Cloud Computing Platforms*.
- [75] A. Uta, A. Custura, D. Duplyakin, I. Jimenez, J. Rellermeyer, C. Maltzahn, R. Ricci, and A. Iosup. Is big data performance reproducible in modern cloud networks? In *17th* {*USENIX*} *Symposium on Networked Systems Design and Implementation (*{*NSDI*} 20), pages 513–527, 2020.
- [76] E. Van Eyk, L. Toader, S. Talluri, L. Versluis, A. Ut,a, and A. Iosup. ˘ Serverless is more: From paas to present cloud computing. *IEEE Internet Computing*, 22(5):8–17, 2018.
- [77] Y. Wadia. *AWS Admin.–The Definitive Guide*. Packt Publishing, 2016.
- [78] Y. Wadia. *AWS Administration-The Definitive Guide: Design, build, and manage your infrastructure on Amazon Web Services*. 2018.

- [79] A. Wang, J. Zhang, X. Ma, A. Anwar, L. Rupprecht, D. Skourtis, V. Tarasov, F. Yan, and Y. Cheng. Infinicache: Exploiting ephemeral serverless functions to build a cost-effective memory cache. In *2020* {*USENIX*} *Conference on File and Storage Technologies (*{*FAST*} 20).
- [80] L. Wang, M. Li, Y. Zhang, T. Ristenpart, and M. Swift. Peeking behind the curtains of serverless platforms. In *2018* {*USENIX*} *Annual Technical Conference (*{*USENIX*}{ATC} 18), pages 133–146, 2018.
- [81] L. Wang, J. Zhan, C. Luo, Y. Zhu, Q. Yang, Y. He, W. Gao, Z. Jia, Y. Shi, S. Zhang, et al. Bigdatabench: A big data benchmark suite from internet services. In *2014 IEEE 20th international symposium on high performance computer architecture (HPCA)*.
- [82] X. Wang, Y. Niu, F. Liu, and Z. Xu. When fpga meets cloud: A first look at performance. *Transactions on Cloud Computing*, 2020.
- [83] O. Yildiz, M. Dorier, S. Ibrahim, R. Ross, and G. Antoniu. On the root causes of cross-application i/o interference in hpc storage systems. In *2016 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*, pages 750–759. IEEE, 2016.
- [84] T. Yu et. al. Characterizing serverless platforms with serverlessbench. In *Proceedings of the 11th ACM Symposium on Cloud Computing*, 2020.
- [85] T. Zhang, D. Xie, F. Li, and R. Stutsman. Narrowing the gap between serverless and its state with storage functions. In *Proceedings of the ACM Symposium on Cloud Computing*, pages 1–12, 2019.
- [86] W. Zhang, V. Fang, A. Panda, and S. Shenker. Kappa: a programming framework for serverless computing. In *Proceedings of the 11th ACM Symposium on Cloud Computing*, pages 328–343, 2020.

#### ARTIFACT APPENDIX

#### A. Abstract

Our artifact packages the data that can be used to reproduce all the results in the paper. Additionally, it also contains the scripts to launch the benchmarks and carry out the experiments on AWS Lambda serverless platform. The artifact is available at the following link:

### https://zenodo.org/record/5539888

It includes the following:

- The benchmarks FCNN, THIS, and SORT.
- Data containing write time, read time, compute time, start time, and end time per function invocation for all the experiments.
- Scripts to install the benchmarks and set up the experiments.
- Scripts to plot the data presented in the paper.

Multiple runs are performed for each of the experiments, with invocation concurrency varying up to 1000, and AWS Lambda memory ranging from 2 GB to 3 GB.

### B. Artifact check-list (meta-information)

- Algorithm: Staggering Lambda invocations to reduce I/O contention.
- Program: Serverless benchmarks THIS, Sort, and FCNN (included in the artifact).
- Data set: The data set required to set-up the benchmarks are included. Data generated through experiments, containing I/O time, compute time, and execution time of serverless functions are included in the artifact.
- Run-time environment: Python3.6 with *boto3* and *awscli*. AWS is invoked for spawning serverless functions from a Ubuntu 18.04.4 LTS server.
- Hardware: AWS Lambda serverless platform, AWS S3, AWS EFS, and AWS EC2.
- Metrics: I/O time, compute time, wait time, and service time.
- Output: Start time, end time, I/O time, and compute time.
- Experiments: Primarily of two types AWS Lambda with S3 as a storage, and AWS Lambda with EFS as a storage.

EFS is experimented in different forms including high throughput mode, high capacity mode, using different directories per functions, and staggering function invocations. Also I/O performance is studied on AWS EC2 virtual machines.

- How much disk space required (approximately)?: 7 GB
- Publicly available?: Yes

#### C. Description

This artifact measures the I/O (read and write) performance of a widely used serverless platform, AWS Lambda. Specifically, we look into the I/O performance of two widely used serverless storages: (1) AWS S3 (block based storage), and (2) AWS Elastic File System (a file system based storage). We benchmark the system with three widely used serverless applications: THIS, Sort, and FCNN. The artifact can be accessed at: https://zenodo.org/record/5539888.

#### D. Installation

To set up the benchmarks and experiments, *boto3* must be installed and *awscli* should be configured with the user's AWS account credentials. This will allow the user to set up and directly export the benchmark deployment packets to AWS via the *aws lambda createfunction* command. More details on installation is provided in the *README.md* file in the artifact.

#### E. Evaluation and expected results

All results from Fig.2 – Fig.13 are expected to be reproduced by the data in the artifact.

