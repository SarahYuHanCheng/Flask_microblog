#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/errno.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include<time.h>
#define PORT 8000
#define BACK_LOG 10

struct paddle
{
    int len;
    int width;
    int x_pos;
    int paddle_move;
    int old_y_pos;
    int new_y_pos;
}paddle_A, paddle_B;

struct ball
{
    int radius;
    int speed[2];
    int old_x_pos;
    int new_x_pos;
    int old_y_pos;
    int new_y_pos;
}ball;

struct score
{
    int score;
    int cpu;
    int mem;
}score_A, score_B;

int WIDTH = 800;
int HEIGHT = 400;
int gametime=30;
void init(){
    
    // init paddle_A
    paddle_A.len=(int)ceil(HEIGHT/3);
    paddle_A.width=8;
    paddle_A.x_pos= paddle_A.width/2-1;
    paddle_A.new_y_pos = HEIGHT/2;
    
    // init paddle_A
    paddle_B.len=(int)ceil(HEIGHT/3);
    paddle_B.width=8;
    paddle_B.x_pos= WIDTH+1-paddle_B.width/2;
    paddle_B.new_y_pos = HEIGHT/2  ;
    
    // ball
    ball.radius =20;
    // ball.speed = [(rand()%3)+2,(rand()%3)+1];
    ball.speed[0] = (rand()%3)+2; //2~4
    ball.speed[1]=(rand()%3)+1; //1~3
    ball.new_x_pos = WIDTH / 2;
    ball.new_y_pos = HEIGHT/2;
    
    printf("%d,%d\n",ball.speed[0],ball.speed[1] );
    return;
}
void *myThreadFun(void *vargp)
{
    int cnt =10000000;
    while (cnt>0) {
        sleep(0.1);
        printf("Check Thread \n");
        cnt-=1;
    }
    
    return NULL;
}
#define SERV_PORT 8000
#define MAXNAME 1024

int max_clients=2;
int player_list[2];
extern int errno;
int client_list[2];
const char * del = ",";

void send_to_players(char* msg_player, int connectfd){
    printf("send_to_players: %s",msg_player);
    char buff[4096];
    int n;
    char buff_int[512];
//    sprintf(buff_int, "%d",ball_pos );
//    strcat(msg_player,"server:");
//    strcat(msg_player,buff_int);
    
    for (int i = 0; i < max_clients; i++) {   
            //if position is empty  
            if( client_list[i] == 0 ) {  
               break;   
            }else{

                if(write(client_list[i],msg_player,strlen(msg_player)) == -1){
                    printf("send msg error: %s \n",strerror(errno));  
                }else{
                    printf("send ball to client %d\n",client_list[i]); // send ball pos ok, reset barrier
                    for (int i = 0; i < (sizeof(player_list)/sizeof(player_list[0])); i++)   
                    {   
                        player_list[i] = 0;   
                    }   
                }   
            }
    }
   
    while(1){ // get paddle move
            printf("recv while\n");
            for (int i = 0; i < max_clients; ++i)
            {
                if( client_list[i] != 0 ) {
                    if((n = read(client_list[i],buff,4096)) > 0){
                        buff[n] = '\0';
                        printf("recv msg from client 0: %s\n",buff);
                        // break;
                    }
                }
            }
            
            if((n = read(client_list[0],buff,4096)) > 0){
                buff[n] = '\0';
                printf("recv msg from client 0: %s\n",buff);
                break;
            }
        }
    
    return;
}
void play(char* msg_player, int connectfd){
     printf("play\n");
    send_to_players(msg_player,connectfd);

    return;
}
void game_handle_connection(char* msg_player, int connectfd){
    
    clock_t start, now,duration;
    start = clock();
    
    duration = ((double)(clock() - start) / CLOCKS_PER_SEC);
    
    while(duration <30){
        play(msg_player,connectfd);
        printf("in handle, duration: %f \n",duration);
    }
    return;
}
void split_msg(char ** after_split, char * msg, const char* del){
    char *s = strtok(msg, del);
    while(s != NULL){
        *after_split++ = s;
        s = strtok(NULL, del);
    }
}


void server(){
    int listenfd,connectfd;
    struct sockaddr_in server;
    struct sockaddr_in client;
    pid_t childpid;
    socklen_t addrlen;

    
    char buff_w[]="sen to cli ok";
    char buff[2048];
    listenfd = socket(AF_INET,SOCK_STREAM,0);
    if(listenfd == -1){
        perror("socker created failed");
        exit(0);
    }
    int option;
    option = SO_REUSEADDR;
    setsockopt(listenfd,SOL_SOCKET,option,&option,sizeof(option));
    bzero(&server,sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);
    server.sin_addr.s_addr = htonl(INADDR_ANY);
    if(bind(listenfd,(struct sockaddr *)&server,sizeof(server)) == -1){
        perror("Bind error!");
        exit(1);
    }
    if(listen(listenfd,BACK_LOG) == -1){
        perror("listend error");
        exit(1);
    }
    printf("waiting for clinet's request.....\n");
    char * arr[3];
    
    while(1){
        int n,i;
        addrlen = sizeof(client);
        connectfd = accept(listenfd,(struct sockaddr*)&client,&addrlen);
        // close(listenfd); //why? 0925
        if(connectfd == -1){
            perror("accept error");
            exit(0);
        }else{
            printf("client connected\n");
        }
        for (i = 0; i < max_clients; i++)   
        {   
            //if position is empty  
            if( client_list[i] == 0 )   
            {   
                client_list[i] = connectfd;   
                printf("Adding to list of sockets as %d\n" , i);   
                break;   
            }   
        }
        if((n = read(connectfd,buff,4096)) > 0){ // get client info
            buff[n] = '\0';
            printf("recv Info from client: %s\n",buff);
            split_msg(arr,buff,del);
            
            if(strtoumax(arr[0],NULL,10)==1){
                printf("left player in\n");
                player_list[0]=1;
                if (player_list[1]!=1){
                    continue;
                }
            }else if(strtoumax(arr[0],NULL,10)==2){
                printf("right player in\n");
                player_list[1]=1;
                if (player_list[0]!=1){//both arrived
                    continue;
                }
            }
            // break;
        }   
       
            //memset(buff,'\0',sizeof(buff));
        game_handle_connection(buff_w,connectfd);
            
        printf("end game\n");
        close(connectfd);
        close(listenfd);
        exit(0);
        // }else if(childpid < 0)
        //     printf("fork error: %s\n",strerror(errno));
        
        

    }
    return ;
    
}
int main(){
    init();
    for (int i = 0; i < max_clients; i++)   
    {   
        client_list[i] = 0;   
    }   
    pthread_t thread_id;
    printf("Before Thread\n");
    pthread_create(&thread_id, NULL, myThreadFun, NULL);
    // pthread_join(thread_id, NULL);
    pthread_detach(thread_id);
    printf("After Thread\n");
    server();
    
    exit(0);
    
    return 0;
    
}
