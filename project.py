
from cmath import atan, pi, sqrt
from math import atan2, fabs
from random import randint, random
from time import sleep
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtlesim.srv import Spawn
from turtlesim.srv import Kill
from std_srvs.srv import Empty

global tsample
tsample=0.005

class my_node(Node):
    global x,y,theta
    x,y,theta=float(randint(1,10)),float(randint(1,10)),random()*3.14
    global flag
    flag=False
    def __init__(self):
        super().__init__("turtle")
        print("node started")
        self.pub1=self.create_publisher(Twist,"/turtle1/cmd_vel",10)
        self.create_subscription(Pose,"/turtle1/pose",self.sub_call,10)
        self.clientsp=self.create_client(Spawn,"/spawn")
        self.clientkill=self.create_client(Kill,"/kill")
        self.service_clientsp(x,y,theta,"turtle_x")
        self.service_client_kill("turtle404")
        self.client=self.create_client(Empty,"/clear")
        self.service_clientclc()
        #self.create_timer(tsample,self.PID)
        self.create_timer(tsample,self.timer_call)


        self.output=[0.0,0.0]
        self.pos=Pose()
        self.rng_y=y
        self.rng_x=x
        self.name_rng="turtle_x"
        

    def sub_call(self,msg):
        self.pos=msg
       # print(f"x: {msg.x} y: {msg.y} theta: {msg.theta}")

    def service_clientsp(self,x,y,theta,turtle_name):
        
        while self.clientsp.wait_for_service(1)==False:
            self.get_logger().warn("wating for server")

        request=Spawn.Request()
        request.x=x
        request.y=y
        request.theta=theta
        request.name=turtle_name
        
        self.clientsp.call_async(request)

    
    def traject(self,x_trgt=5.4,y_trgt=5.4):
        x_current=round(self.pos.x, 4)
        y_current=round(self.pos.y, 4)
        theta_current=round(self.pos.theta,4)
        theta_req=atan2((y_trgt-y_current),(x_trgt-x_current+0.0000001))
        #print(theta_req)       
        theta_req=round(theta_req,4)
        theta_polar=theta_req-theta_current
        if fabs(theta_polar) >=pi:
            if(theta_polar>0):
                (theta_polar)=(theta_polar)-2*pi
            else:
                (theta_polar)=(theta_polar)+2*pi
        R_polar=sqrt(pow((x_trgt-x_current),2)+pow((y_trgt-y_current),2)).real
        print(f"R={R_polar} , Angle={theta_polar}")
        return [R_polar,theta_polar]
    
    def service_client_kill(self,turtle_name):
            request=Kill.Request()
            request.name=turtle_name
            self.clientkill.call_async(request)

    def service_clientclc(self):
        
        while self.client.wait_for_service(1)==False:
            self.get_logger().warn("wating for server")

        request=Empty.Request()
        
        
        futur_obj=self.client.call_async(request)
    #def future_call(self,future_msg):
        
        #    print(f"response is, {future_msg.result().name}")
    def timer_call(self):
        self.output=self.traject(self.rng_x,self.rng_y)
        motion=Twist()
        diff=3.14-self.pos.theta
        
            
        motion.linear.x=self.output[0]
        motion.angular.z=(self.output[1])*2
        print(self.output[1])
        
        if self.output[0] <= 0.5:
            self.service_client_kill(self.name_rng)
            self.rng_x,self.rng_y,theta=float(randint(1,10)),float(randint(1,10)),random()*3.14
            self.name_rng="turtle"+str(randint(0,1000))
            self.service_clientsp(self.rng_x,self.rng_y,theta,self.name_rng)
            self.service_clientclc()
            
            

            
            

        #x.angular.z=self.outa
        self.pub1.publish(motion)


def main(args=None):
    rclpy.init(args=args)

    node=my_node()
    rclpy.spin(node)
    rclpy.shutdown()
main()



