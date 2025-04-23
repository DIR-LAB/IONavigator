# Mandatory Access Control for Shared HPC Clusters: Setup and Performance Evaluation

Mathieu Blanc *CEA/DAM/DIF Bruyères-le-Châtel 91297 Arpajon Cedex, France mathieu.blanc@cea.fr*

# ABSTRACT

*Protecting a HPC cluster against real world cyber threats is a critical task, with the increasing trend to open and share computing resources. As partners can upload data that is confidential regarding other partners, a company managing a shared cluster has to enforce strong security measures. It has to prevent both accidental data leakage and voluntary data stealing. When using an operating system based on Linux, the offered protections are difficult to set up in large scale environments. This article presents how to use the Mandatory Access Control feature of SELinux in order to guarantee strong security properties for HPC clusters. The proposed solution is based on the use of the Multi-Category System, the confinement of user profiles and the use of a dual SSH server. The issues encountered during the implementation and the most difficult technical points are presented. Finally, this paper shows experimental results about the performance of our solution and the impact on a large scale cluster.*

#### KEYWORDS: HPC Clusters, Access Control.

# 1. INTRODUCTION

The security of computing clusters operating systems is often overlooked, the focus being on achieving the best performance. However, these computing architectures are often shared between several partners, and companies running large HPC clusters often sell computing time to interested third parties. The data and computation performed on these clusters are almost always confidential for the party using them. Of course they have to trust the cluster administrator, but they will not necessarily trust other parties using the same computing resources. Hence it is the responsibility of the company that owns the computing facil-

Jean-François Lalande *Centre-Val de Loire Université LIFO, ENSI de Bourges 88 bd Lahitolle, 18020 Bourges, France jean-francois.lalande@ensi-bourges.fr*

ity to ensure that proper security policies and mechanisms are in place in order to protect the access to the data and processes of all the partners and clients.

High performance computing architectures are extremely specialized, compared to general computing facility. They present specific security issues and properties. As outlined by William Yurcik [1], these issues must be addressed in a way that is relevant, with a combination of techniques either general or specific to cluster architectures. As a simplified example, a cluster can be perceived in two different ways: either as a whole particular system connected to other networks and with particular needs in terms of access, or as a combination of heterogeneous systems (login nodes, computing nodes, storage nodes and so on). In this distributed view of a cluster, interactions between nodes must be protected and monitored [2]. However, the security of cluster cannot rely solely on the observation of the network between nodes. It is also essential to control what operations are done on the nodes.

The goal of this paper is to present how we addressed different security needs on a shared computing platform and to measure their impact on performance. The guaranteed security properties are strong and a strong hypothesis is made: a malicious user can exploit a system vulnerability and gain administrator privilege. Even in this case, the proposed security measures should keep the intruder confined and the other partners protected.

First, related works that deal with security of HPC and performance issues are briefly described. Second we present the various objectives of the security policy that have been implemented. Then, the section 4 deals with our configuration of SELinux and how it matches our security goals. The following section explains the issues encountered during the implementation of our SELinux policy on our experimental computing clusters and the remaining issues with this implementation. Finally the paper describes the secured production clusters and studies the performance impact of the security solution.

# 2. STATE OF THE ART

#### 2.1. Security-Enhanced Linux

Security-Enhanced Linux or SELinux is a security mechanism integrated in the Linux kernel [3]. Traditionally, the security of Unix-like operating systems relies on the Discretionary Access Control (DAC) [4]. In this model, users control the access permissions on their own files. But SELinux provides a Mandatory Access Control (MAC) mechanism [5][6]. With MAC, access permissions are enforced by a separate access control policy written by a security administrator. SELinux operates by associating security contexts to processes and files, and then the access control policy states how security contexts are allowed to interact with each other. A security context is normally composed of three mandatory identifiers and two optional ranges. The three identifiers are the SELinux user (independent from a system user), the role and the type. The two ranges are the levels from the Multi-Level Security (MLS) model and the categories from the Multi-Category Security (MCS) model [7, 8].

The main benefit of an operating system controlled by SELinux is a strong protection mechanism extremely hard to defeat. In a previous work [9], we presented a honeypot project, i.e. a dedicated computer exposed to attacks from the Internet. It has been deployed for two years with the possibility for intruders to obtain an access. Secured by SELinux, the honeypot was never reinstalled and the system has never been damaged. It demonstrates that even if a malicious user has access to a SELinux protected cluster, the corruption of the system and the steal of information become a hard challenge. The advantages and drawbacks of SELinux have been widely debated, but everyone agrees on one point: SELinux can be very complex to deploy if a specific policy has to be created.

#### 2.2. Security in HPC

One of the first approach to integrate MAC in clusters was DSI [10] by Ericsson. They were the first to provide a policy deployment framework specifically aimed at HPC architectures. The main drawback was that they conceived their own policy language, and were far from SELinux in terms of features. Besides, the development of DSI has been discontinued a long time ago, hence it is not designed to work on recent Linux distributions.

Some companies offer preconfigured operating systems for HPC clusters, like NimbusOS from Linux Labs International. Unfortunately, no precise description of the policies is available. The proposed policy may be the standard targeted SELinux policy that provides confinement for network services but no special rules to confine the users. Regarding our objectives, such a solution is not sufficient. As described latter in section 3, we want to guarantee isolation even if a malicious user gains administrator privileges. Moreover, such a solution imposes the use of a particular operating system with integrated security, whereas we already have our own cluster operating system on which we want to enhance the security.

#### 2.3. Performance and Virtualization

For the HPC community, the performance of a cluster is an important subject of investigation, especially if security measures are implemented. In [11], the XEN paravirtualization technique is evaluated on MPI processes run on a cluster of four nodes, each with four processors. The main result is that there is no significant impact of the virtualization on the performance. Nevertheless, the deployment of such a technology is not trivial and the security benefit is not clear contrary to the benefits brought by SELinux.

A similar work to the one proposed in this paper, but based on virtualization techniques, is described in [12]. Their goal is to achieve strong isolation between users in what they called "containers". They discuss how to set up containers to obtain a good trade-off between performance and isolation. This isolation is applied to both resources (e.g. files) and system objects (e.g. memory, cpu). The results compare different virtualization techniques compared to two standard Linux kernels. Depending on the benchmark software, the results shows a loss from 0% to 30% in disk performance and no difference for network throughput. The results are good for lightweight virtualization techniques such as VServer. As the kernel is shared, the system calls have no extra cost. Nevertheless, the set up of a container requires to include all the data and the binaries used by the user that will be jailed in this container. This set up is difficult and the reconfiguration of such a system for a new partner using the cluster cannot be done easily.

## 2.4. Synthesis

The goal of this paper is to present the integration of MAC in an existing operating system for HPC clusters, with several constraints: 1) integrate the security objectives described in section 3; 2) do not modify the operating system, in particular the kernel, or else commercial support is not assured; 3) have a minimal impact on performances.

As we explained previously, related works do not cover all the security requirements for our clusters, thus we will propose a new solution based on SELinux, as it is a standard part of the Linux RedHat Enterprise kernel. As the default policy in this operating system is the targeted policy from RedHat, it does not cover any of our security objectives which justifies to conceive new policy modules to introduce the required security properties. In particular, the targeted policy does not provide confidentiality between users, and does not address the issue of access control on network file systems like NFS and Lustre. In order to present our solution, section 3 gives further details on our objectives, and section 4 describes the principles and the design or our solution.

# 3. SECURITY OBJECTIVES

In this section, we present the security goals for an experimental shared HPC cluster. These goals are the basis of the security policy that will be applied by SELinux. They can be resumed in four points:

- Ensure the confidentiality of data uploaded by partners (isolation in [12]);
- Confine user profiles and services so that a malicious elevation of privileges does not compromise the security of the operating system;
- Differentiate public SSH access and administrator SSH access;
- Secure and control interactions with batch schedulers and authentication mechanisms (Kerberos in our framework).

## 3.1. User Containers and Data Confidentiality

Users from the same projects should be able to exchange files freely. Hence there is a particular set of Unix groups called "containers". These containers represent people working on the same project or users that are granted access by the same administrative procedure (for example a national research agreement). In these containers, accidental leakage of information due to incorrect permissions is considered harmless.

Definition 3.1 (Container) *In a container* A*, with* (a1, a2) ⊂ A, a1 *accessing a file* f *belonging to* a2 *does not break the confidentiality of file* f.

which means, in terms of confidentiality:

Definition 3.2 (Confidentiality) *Data confidentiality means that a user* a *from container* A *must not be able to read a file* f *belonging to a user* b *from container* B, *whatever permissions are set on* f.

Of course, this does not mean that any user can access all the files of all other users in the same container. Typically, a MAC mechanism will confine users in their container, and then inside a container users can restrict access to their own files with DAC permissions.

## 3.2. Confined Users and Services

Users and services should be confined in order to prevent any tampering with the security mechanisms. A first example is a malicious hacker exploiting a flaw in a network service in order to gain administrative access to a login node. Exploiting a flaw should not allow him to break the data confidentiality of another container. Another example is a legitimate user downloading a malicious code from the Internet and using it to gain administrative privileges on his node. Even if this succeeds, this user should not be able to access files outside his container.

Definition 3.3 (Confinement) *Any person gaining administrative privileges on a system must not be able to break the confidentiality property, either legitimate user or external attacker.*

There are still some limitations with this kind of confinement. They will be discussed in section 5.

# 3.3. SSH Access

There should be two different points of access on the cluster nodes as represented on figure 1: a public access for standard users, and an administrative access reserved to system administrators. These accesses are always set up with a ciphered protocol like SSH. Even in the case of a vulnerability exploited in the server that gives an administrative access to an attacker, the public access should never allow users to configure the security mechanisms.

Of course interactive user access is not always enabled. For example, there are some parts of the cluster like computing nodes where standard user access has to be disabled. These nodes should only be accessed through the batch scheduler as shown on figure 1. The same restriction goes for the storage nodes, accessible only through mounted network file systems. These are only examples, as each cluster has its specific areas.

## 3.4. Schedulers and Authentication Services

The security mechanisms implemented on the node (like SELinux) should ideally protect the batch scheduler mechanism and the Kerberos authentication services. For the scheduler, both the job submission and the command execution on computing nodes should be taken into account by the security mechanism. It is especially important to pro-

![](_page_3_Figure_0.png)

Figure 1. A Typical Cluster

Storage nodes

tect and confine the job execution service, as it is the equivalent of an SSH access on all cluster nodes. For example, if there is a vulnerability on the cluster operating system, a malicious user could launch a command exploiting it on all nodes with just a batch submission. That is why user jobs should be executed in a confined context on the computing nodes. For authentication services, users credentials should be protected with a MAC mechanism. For example, the Kerberos ticket caches of a particular user should be protected in a way that ensures that only users from the same container may have access to it, even if the system is compromised. In this way, it is possible to avoid that a malicious user steals another user's credentials in order to authenticate as him and try to access his files. Figure 2. Cluster Policy Architecture source files. A binary policy module file can directly be distributed and loaded. With the semodule command, an additional binary module can be merged with a *base* module (containing base types and policy) and produce the new binary policy. This can be done at any time on a running system and the policy is loaded dynamically. Leveraging this feature, our approach is to produce only binary modules, without modifying the Red Hat Linux Enterprise 5.4 targeted policy. The two modules that we wrote implement the following objectives (cf. figure 2) : ccc_guest implements the confined user profiles called *guest* for SSH access and *xguest* for graphical access; sshd_admin implements the two lev-

4. PROPOSED SECURITY SOLUTION

This section describes the policy that has been designed to answer the security goals exposed in section 3. First the modularity of the solution is exposed, using the new SELinux module architecture. Then, the section describes the methodology that allows to write the policy file. At the end, we discuss the possible limitations of the proposed solution and we show that the implementation is quite flexible.

## 4.1. Implementation as Policy Modules

Back in 2001, when SELinux was introduced in the Linux kernel as a patch [13], the policy was only composed of a large monolithic text file. This file was written according to the SELinux grammar, and compiled by a tool called checkpolicy in order to obtain a binary representation of the policy. This binary blob was then loaded into the kernel, and then applied as defined by the mode of SELinux, either *permissive* or *enforcing*.

The process of writing a policy has greatly evolved since then. The policy has first been split into several text files, that were combined in order to produce the policy file before compilation. After that, binary modules were introduced. Thanks to this modular binary policy representation, it is not necessary anymore to install all the policy els of SSH access, public and administrative. Specific security contexts are associated with two separate SSH servers.

#### 4.2. Policy Build Process

There are two ways to get the SELinux policy for a piece of software. The ideal way is to integrate the policy definition in the application development process. It produces a policy that is both consistent and complete. However, this way requires that the developers know exactly what their applications do from an operating system point of view. A more realistic way is a learning process like described in [14]. A system is set up with the base SELinux policy running in *permissive* mode. This means that SELinux will not forbid any action, it will only log system calls that should have been forbidden. Then all the software that need specific rules are run in the most typical usage scenarii producing relevant SELinux logs that can be converted into relevant rules. In this process, the administrator should review carefully the produced rules. Indeed, the learning process will eventually capture useless rules that can expose critical parts of the operating system and make the confinement ineffective.

In order to write our new SELinux policy modules, we followed the second approach as we do not necessarily have access to the source code of all applications running on our shared clusters. In details, the systematic approach we used in the process of writing our SELinux policy was as follows: 1) Load the default "targeted" policy on our test platform, based on RedHat Enterprise Linux 5.4; 2) Load an initial or development version of our policy modules; 3) Run applications in standard usage scenarii; 4) Identify execution issues and broken functionalities; 5) Review SELinux logs (by default in /var/log/audit/ audit.log); 6) Convert the relevant logs into rules using audit2allow; 7) Review the rules and integrate the relevant one in sources of policy modules; 8) Go back to step 2.

Each type of node in the cluster is operated to generate its own SELinux logs. A cleaner process could be to audit all the nodes of the cluster, centralize the logs and perform correlation with techniques and tools such as proposed in [15] which can guarantee a more unified policy. Nevertheless, auditing the nodes independently guarantees to get the most accurate policy.

#### 4.3. The Policy Components

The resulting policy of our writing process is composed of the standard "targeted" policy and two modules called ccc_guest and sshd_admin.

By default, with the targeted policy, all users are placed in the context (user_u, system_r, unconfined_t). The module proposes to specific security contexts to confined the users: ccc_guest and ccc_xguest. The first one is associated to SSH connections, and the second one is associated to X11 sessions. They are originally derived from the guest and xguest profiles of Fedora 10, provided by Dan Walsh [16] and limit the administrative privileges accorded to users.

For example, a standard user logged on the system via SSH will have the context (ccc_guest_u, ccc_guest_r, ccc_guest_t). Trying to exploit a vulnerability in any system command or service, a malicious user may obtain a root access. Nevertheless, he will not be allowed to interact with other security contexts of the system as the policy does not allows (ccc_guest_u, ccc_guest_r, ccc_guest_t) to do so. Listings 1 and 2 are a sample of the definition of the guest user profile.

In the targeted policy, the SSH server is not associated to a particular context, it is actually executed in the unconfined_t type. As the SSH service must be accessible to all the cluster partners from the Internet, it is heavily exposed to attacks. Moreover, any process in the same context can attack the SSH server. The proposed policy module sshd_admin answers two goals. Firstly

# Listing 1. Sample from **ccc_guest.if** ✞ ☎

```
interface('cea_unprivileged_user', '
   userdom_unpriv_login_user($2)
   userdom_basic_networking_template($2)
   kernel_read_network_state($1)
   corenet_udp_bind_all_nodes($1)
   corenet_udp_bind_generic_port($1)
   corenet_tcp_bind_all_nodes($1)
   corenet_tcp_bind_generic_port($1)
   cea_userdom_login_user($2)
 ')
✡✝ ✆
```
# Listing 2. Sample from **ccc_guest.te** ✞ ☎

```
policy_module(ccc_guest, 1.0.1)
cea_unprivileged_user(ccc_guest_t, ccc_guest);
cea_unprivileged_user(ccc_xguest_t, ccc_xguest);
userdom_restricted_xwindows_user_template(
    ccc_xguest);
gen_user(ccc_guest_u, user, ccc_guest_r
    ccc_xguest_r, s0, s0 − mls_systemhigh,
    mcs_allcats)
```
✡✝ ✆

we want to confine the SSH server so that if an attacker exploits a vulnerability in it, he will only reach a confined profile. Secondly, the obtained SELinux roles for the SSH server should be limited to what is strictly necessary. A first context sshd_public_t has been created for the partner SSH access. This context can only transit to the ccc_guest_t type. The second context sshd_admin_t is reserved for administrative access, and can transit to the unconfined_t type to get full access on the processes and resources in this context. The targeted policy and the proposed policy including the ccc_guest and sshd_admin are compared in figure 3. Nevertheless, this two modules do not achieve one of the security goals: the isolation of users that is presented in the next section.

#### 4.4. Users Isolation

As presented briefly in section 1, MCS stands for Multi-Category System. This is a part of the security model from Bell and LaPadula [5]. The principle is to associate categories to users and files. Then to read a particular file f, a user U must be associated at least to all the categories of f. In the targeted policy for SELinux, the standard available range of categories is c0 to c1023, thus a total of 1024. In order to create containers for users, as defined in section 3,

![](_page_4_Figure_14.png)

Figure 3. Two Levels of SSH Access.

![](_page_5_Figure_0.png)

Figure 4. File Access Control With MCS.

a category is associated to a set of users who have the same origin (specific partnership, a research program, a particular university). This solution provides isolation between users of different categories, as shown on figure 4. It supposes that each file should only have one category and that DAC permissions are well set up.

The categories provide an additional benefit to administrate finely the rights of a specific partner in one container of category c1. A special category c1000 could be applied to this partner and some files of the partner: the consequence is that this partner will be able to read any file that has category c1 but no other partner of the container will be able to read the file tagged with categories c1, c1000. Thus, the number of subsets that isolates users and files is very high (21024) and sufficient to implement any isolation policy.

Again, a malicious user obtaining a root access when exploiting a software vulnerability will be confined in its category and thus will not be able to access other categories than the set he was assigned when logging in. It reinforces the security provided by the two created policy components.

# 5. COMPLEX CHALLENGES

The section that follows presents the more complex technical issues that have been encountered in the process of writing the proposed SELinux configuration.

### 5.1. NFS Homes and User Containers

The security contexts and categories of files are stored in special extra attributes on the disk. In a large HPC cluster, the data is accessed via networks mounts. The support of such extra attributes across the network, for example over NFS, is very experimental as pointed in a previous work [17] and thus not available on the RHEL 5.4 operating system. It is possible to apply a specific context to a file system with the mount command, as shown in this example:

```
mount −t nfs −o context=system_u : object_r :
    nfs_t : c1 server : / home / home / c1
```
However, this technique does not work because of the way the Linux kernel handles the NFS filesystems. When many filesystems are mounted from the same IP address, the kernel applies the same options for all the mount point. Thus it is not possible to specify different security contexts for several NFS filesystems mounted from the same server.

To solve this issue, a workaround is proposed: the context and MCS category is applied directly on a local directory, and the NFS filesystem is mounted under that directory. For example, the experimental cluster uses paths like /c1/home/user. Here the c1 directory has the category c1. home is the mount point for the sub directory of the NFS filesystem containing the home directories for users in the c1 container. This workaround should only be temporary. Specification for *Labeled NFS* have been published [18], and work on the integration of SELinux in NFSv4 is in progress [19].

## 5.2. Lustre

The Lustre filesystem driver seems to support SELinux labels and categories. Our investigations showed that Lustre interacts very badly with SELinux which confirms what reports [20]. For example, when first mounting a Lustre filesystem, the files are seen as with the security context unlabeled_t, which is actually the default type when SELinux contexts are not supported. When creating a new file, it receives the type file_t, the default type when contexts are supported. But when remounting the filesystem, the newly created file will be unlabeled like the other files. Moreover, as it is not possible to mount a sub directory from a Lustre mount point, we cannot apply the same workaround as for NFS filesystems. At this time a Lustre filesystem has to remain declared as a shared zone, not isolated. The only way to resolve this issue is to implement a proper support for SELinux in the Lustre driver, which is not in the current road map [21].

# 5.3. Remaining Issues

As powerful and configurable as SELinux is, it is always important to remind that it cannot protect against certain threats. Essentially, in the case of a Linux kernel vulnerability, the confinement mechanism of SELinux can be broken, as SELinux is a part of the kernel. So far, several pieces of code have been published that exploit Linux kernel vulnerabilities and at the same time defeat the SELinux confinement [22]. However, with SELinux it is possible to block the exploitation vector for a kernel vulnerability, or to mitigate the result of a successful attack. Regarding the exploit codes that have been published for recent kernel vulnerabilities, they usually only give more privileges to the shell of the user running the exploit. For example, the widely known exploit code for the vulnerability in the sys_vmsplice() kernel function only changes the UID of the user shell to 0 (the root UID). We tested this vulnerability and the user shell under root UID remains in the ccc_guest context and is still confined.

Table 1. Some production clusters at CEA.

|  | Computing cluster | Visu. cluster |
| --- | --- | --- |
| Total nodes | 1140 | 50 |
| CPU/node | 2 Intel Nehalem Quad | 2 Intel Xeon 5450 |
| RAM/node | 24 Go | 64/128 Go |
| Network FS | 500 To | 100 To |
| User accounts | ≈ 4000 |  |
| Avg. run. jobs | 100-150 | 10 |
| Avg. qu. jobs | 100-1000 | N/A |

# 6. EXPERIMENTAL RESULTS

Before we reach the conclusion of this article, we will describe the HPC clusters were our SELinux policy is being deployed, and present results about the impact of SELinux on the I/O performance of a computing node.

## 6.1. The Shared CEA Clusters

The SELinux configuration proposed in section 4 is currently planned for deployment on two clusters. The first cluster is dedicated to scientific computing, and is composed of 1068 computing nodes (including 2 interactive nodes), 48 GPU nodes and 24 I/O nodes. It achieves a peak power of 100 Tflops CPU and 200 Tflops GPU. The second cluster is dedicated to data reduction and visualization. It is composed of 38 computing nodes (each node equipped with a Quadro FX 5800), 2 login nodes and 10 I/O nodes. More details are given in Table 1.

#### 6.2. Performance Benchmarks

One of the goal of this paper was to present the performance impact on the cluster of the proposed solution. Several benchmarks has been conducted, essentially on the Input/Output performance on SELinux-enabled computing nodes. Indeed, as SELinux mainly adds checks in system calls, the I/O operations are the greatest points of impact. Two types of benchmark were performed on nodes similar to the nodes of the presented production clusters, with a small Lustre filesystem composed of 1 MDS and 2 OSSs: IOR tests the throughput of MPI Input/Output operations in parallel file systems (separated means that all tasks work on different files, grouped means they work on the same file) and bonnie++ evaluates the performance of operations on file metadata, for example creation and deletion of files.

The figures 5 and 6 show the data throughput. The impact of SELinux is acceptable, less than 10%. On figure 7 the metadata operations per second are evaluated, it shows that SELinux has a great impact on file creation time (about 30%). This test was repeated many times with the same result. As a complementary check we performed the bonnie++ benchmark on a local filesystem and observed a more standard 10% impact from SELinux on file creation time.

![](_page_6_Figure_9.png)

Figure 5. Separated MPIIO Benchmark.

![](_page_6_Figure_11.png)

Figure 6. Grouped MPIIO Benchmark.

This is probably related to the Lustre issue described in section 5.

## 7. CONCLUSION AND FUTURE WORK

In this article, we addressed the issue of confidentiality on a shared cluster, with a solution that offers strong protection. A detailed analysis of the implementation using a SELinux policy has been given. The built policy enforces strong security properties for NFS and SSH services and isolate the users, even if a vulnerability is exploited. Then the paper presented the most complex technical issues encountered and how we propose to mitigate them, as well as the remaining issues. Finally we presented the performance impact of the proposed solution.

Going through this study of the definition and the deployment of a SELinux policy, we were faced with several challenges. First we had to perfect our understanding of the inner working of SELinux and its policy grammar. Then we had to adapt current administrative procedure to comply with the activation of SELinux. Indeed, usual cluster

![](_page_7_Figure_0.png)

Figure 7. Sequential Metadata Benchmark.

administration can sometimes be very contradictory with the most basic rules of the SELinux policy.

The next steps of this work are to solve the incompatibility between Lustre and SELinux, to add the support of contexts on NFS filesystems, and to propose solutions to perform efficiently the regular adaptation of the policy to the new applications deployed on our clusters. For this evolution, the administrator needs new tools to perform safe updates and to verify that the new policy will not introduce security issues.

# REFERENCES

- [1] W. Yurcik, G. A. Koenig, X. Meng, and J. Greenseid, "Cluster security as a unique problem with emergent properties: Issues and techniques," *5th LCI International Conference on Linux Clusters*, May 2004.
- [2] M. Pourzandi, D. Gordon, W. Yurcik, and G. Koenig, "Clusters and security: distributed security for distributed systems," in *International Symposium on Cluster Computing and the Grid*. IEEE, 2005, pp. 96–104.
- [3] S. Smalley, C. Vance, and W. Salamon, "Implementing SELinux as a linux security module," NSA, Tech. Rep., Dec. 2001.
- [4] B. W. Lampson, "Protection," in *The 5th Symposium on Information Sciences and Systems*, Princeton University, Mar., pp. 437–443.
- [5] D. E. Bell and L. J. La Padula, "Secure computer systems: Mathematical foundations and model," The MITRE Corporation, Bedford, MA, Technical Report M74-244, May 1973.
- [6] K. J. Biba, "Integrity considerations for secure computer systems," The MITRE Corporation, Technical Report MTR-3153, Jun. 1975.
- [7] S. Smalley and T. Fraser, "A Security Policy Configuration for the Security-Enhanced Linux," NSA, Tech. Rep., Dec. 2000.

- [8] Frank Mayer, Karl MacMillan, and David Caplan, *SELinux by Example*. Prentice Hall, 2006.
- [9] J. Briffaut, J.-F. Lalande, and C. Toinard, "Security and results of a large-scale high-interaction honeypot," *Journal of Computers, Special Issue on Security and High Performance Computer Systems*, vol. 4, no. 5, pp. 395–404, may 2009.
- [10] M. Pourzandi, A. Apvrille, E. Gingras, A. Medenou, and D. Gordon, "Distributed access control for carrier class clusters," in *Proceedings of the Parallel and Distributed Processing Techniques and Applications (PDPTA '03) Conference*, Las Vegas, Nevada, USA, Jun. 2003.
- [11] L. Youseff, R. Wolski, B. Gorda, and C. Krintz, "Evaluating the Performance Impact of Xen on MPI and Process Execution For HPC Systems," *First International Workshop on Virtualization Technology in Distributed Computing (VTDC 2006)*, pp. 1–1, novembre 2006.
- [12] S. Soltesz, H. Pötzl, M. E. Fiuczynski, A. Bavier, and L. Peterson, "Container-based operating system virtualization: a scalable, high-performance alternative to hypervisors," in *European Conference on Computer Systems*, vol. 41, no. 3, 2007.
- [13] P. Loscocco and S. Smalley, "Integrating flexible support for security policies into the linux operating system," in *Proceedings of the FREENIX Track: 2001 USENIX Annual Technical Conference (FREENIX '01)*. USENIX, Jun. 2001.
- [14] D. Walsh, "A step-by-step guide to building a new SELinux policy module," Red Hat Magazine, 2007.
- [15] Mathieu Blanc, Patrice Clemente, Jonathan Rouzaud-Cornabas, and Christian Toinard, "Classification of Malicious Distributed SELinux Activities," *Special Issue of JCP: Selected Papers of The Workshop on Security and High Performance Computing Systems (SHPCS)*, 2009.
- [16] Dan Walsh, "Confining the User with SELinux," http:// danwalsh.livejournal.com/10461.html, 2007.
- [17] M. Blanc, K. Guérin, J.-F. Lalande, and V. L. Port, "Mandatory access control implantation against potential nfs vulnerabilities," in *Workshop on Collaboration and Security 2009*, W. W. Smari and W. McQuay, Eds. Baltimore: IEEE Computer Society, 2009, pp. 195–200.
- [18] D. Quigley and J. Morris, "MAC Security Label Requirements for NFSv4," IETF, Tech. Rep., Jun. 2008.
- [19] SELinux Project, "Labeled NFS," http://selinuxproject.org/ page/Labeled_NFS, Dec. 2009.
- [20] Jeff Bastian, "files on Lustre filesystem are unlabeled_t," https://bugzilla.redhat.com/show\_bug.cgi?id=489583, Oct. 2009.
- [21] Lustre, "Lustre Roadmap," http://wiki.lustre.org/index.php/ Lustre_Roadmap, Nov. 2009.
- [22] Brad Spengler, "On exploiting null ptr derefs, disabling SELinux, and silently fixed Linux vulns," http://lists.immunitysec.com/pipermail/dailydave/ 2007-March/004133.html, Mar. 2007.

