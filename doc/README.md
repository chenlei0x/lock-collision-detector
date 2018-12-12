
# ocfs2 hot file detector -- o2top

## Requirement and Background

Ocfs2 users complain the performance regression on ocfs2 file system. We suspect that maybe in our customers environment, they are accessing the same file or dir across the multiple nodes.

However, unfortunately, our customers can not detect which files or dirs is a trouble-maker.

Even worse, ocfs2 does not provide a tool to shed the light.

## Ocfs2 design details

### OCFS2 lock model

ocfs2 is a cluster-oriented file system. To guarantee the consistency of file data, ocfs2 use dlm(distributed lock manager) to create and operate a cluster-wide lock(dlm lock). A dlm lock is identified by a unique lock id across the whole cluster, and it provides multiple lock levels.

From the perspective of ocfs2, a dlm lock works as following:

1.  A dlm lock has 3 lock levels: None, Protected Read(PR) and Excluded(EX)

2.  A dlm lock is a node-level lock, not process-level lock. It means that a dlm lock belongs to a node, if you need to prevent multiple task accessing the same lock id which corresponds to the same dlm lock, it should be done by yourself, not dlm.

3.  It works totally like a rw lock. If you want to obtain the read access to the lock, you should acquire the lock id with Protected Read level; If you want to obtain the write access of the lock, you should acquire it with Excluded level; If you release the lock, it’s in a None level.

4.  For one dlm lock, a EX level could only be obtained by one node, PR level could be shared among multiple nodes.

5.  When a node, or a kernel has obtained a dlm lock with PR level, other node could also be granted with PR level lock. But If a node wants to obtains an EX level on the dlm lock, it must wait until all the other nodes that possess any level on the dlm lock releases. If a node has already obtained a EX level on a dlm lock, other nodes trying to obtain any level of this dlm lock must wait until EX level is released.

The ocfs2 kernel module resides on each nodes, and they all strictly follows the rules below,

1.  each inode represents a file on disk.

2.  an inode contains 3 dlm lock, a META dlm lock, an OPEN dlm lock, an RW dlm lock. They are used for different purposes.

3.  If users want to access a file, one or more of dlm locks mentioned above must be lock with proper level.

### Root cause of performance regression

As mentioned above, for a dlm lock, because of the mutex relationship between EX level and PR level, if multiple nodes try to obtain different level of the the dlm lock, their must be nodes that wait for other nodes to release EX level. What’s worse, to access an inode, multiple dlm locks within an inode might be involved.


For a directory, when creating new files or renaming a file within a directory, the EX level lock must be precedingly obtained, which prevents other nodes from accessing it.

### Recommendations

As clarified above, we talked about how ocfs2 internally works, and why dlm locks is a must, though it slows down the access speed.

For users, it’s recommended that,
1.  prevent writing one file from multiple nodes
2.  prevent multiple nodes from accessing the same directory.

## o2top

### Our intention

Though we have provided some recommendations, we still can not guarantee everything goes as we expect. With our software more and more complicated, it can not be completely avoided to write a file from multiple nodes.

As for users, some actions should be taken once they know which files are written from multiple nodes(we call them hot files). But things is not that simple. There is no way to know which are hot files. When they meet ocfs2 performance regression, they don’t know what’s happening.

This tool aims at detecting hot files for users.


### Internal data structures

[See o2top.jpg within current dir]

A LockSpace corresponds to one ocfs2 file system instance which could be mounted on multiple Nodes.

Several nodes might tries to access one dlm lock, as the image shows, Lock 2 is now simultaneously accessed by the 3 nodes.

A Lock represents a dlm lock in one node. As ocfs2 designed, processes on one node shares this Lock instance.

A Shot means the status of one Lock on One Node. As ocfs2 runs, it keeps changing.

A LockSet represents the statistics collected from multiple nodes against one Lock.

A LockSetGroup is a group of LockSet(s) used to ranks LockSet(s) and generates report.


### How o2top work

o2top works in a simple way. It maintains several threads which keep collecting ocfs2 lock info from multiple nodes.

Once a thread gathered all lock info from one Node, it forms multiple Shot(s), each of which corresponds to a dlm lock ID.

Then according Shot’s lock id, each Shot from one Node will be put inside of a Lock. A Lock containes many Shot(s) to describe the trend of itself.

Multiple Lock maybe share the same lock id but they come from different Nodes. Lock(s) with identical lock id will be put in LockSet.

LockSet group will rank the multiple LockSet(s), and pick the top n hot file to generate the final report.

For the detailed usage, please run: o2top --help

# To do

1.  O2top can only show hot files in term of inode number, which is not that convenient for our customers. Would be better go one more step: can we suggest some approach how to turn inode to the absolute path in the filesystem?
    
2.  to do
