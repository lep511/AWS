import time
from multiprocessing import Process, Pipe
import boto3

class VolumesParallel(object):
    """Finds total volume size for all EC2 instances"""
    def __init__(self):
        self.ec2 = boto3.resource('ec2')

    def instance_volumes(self, instance, conn):
        """
        Finds total size of the EBS volumes attached
        to an EC2 instance
        """
        instance_total = 0
        for volume in instance.volumes.all():
            instance_total += volume.size
        conn.send([instance_total])
        conn.close()

    def total_size(self):
        """
        Lists all EC2 instances in the default region
        and sums result of instance_volumes
        """
        print "Running in parallel"

        # get all EC2 instances
        instances = self.ec2.instances.all()
        
        # create a list to keep all processes
        processes = []

        # create a list to keep connections
        parent_connections = []
        
        # create a process per instance
        for instance in instances:            
            # create a pipe for communication
            parent_conn, child_conn = Pipe()
            parent_connections.append(parent_conn)

            # create the process, pass instance and connection
            process = Process(target=self.instance_volumes, args=(instance, child_conn,))
            processes.append(process)

        # start all processes
        for process in processes:
            process.start()

        # make sure that all processes have finished
        for process in processes:
            process.join()

        instances_total = 0
        for parent_connection in parent_connections:
            instances_total += parent_connection.recv()[0]

        return instances_total


def lambda_handler(event, context):
    volumes = VolumesParallel()
    _start = time.time()
    total = volumes.total_size()
    print "Total volume size: %s GB" % total
    print "Sequential execution time: %s seconds" % (time.time() - _start)