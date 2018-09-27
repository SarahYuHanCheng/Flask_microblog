#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

int run (msg){
    return 0;
}
void split_msg(char ** after_split, char * msg, const char* del){
    char *s = strtok(msg, del);
    while(s != NULL){
        *after_split++ = s;
        s = strtok(NULL, del);
    }
}
int main(int argc , char *argv[])
{
    char test_str[4096];

    //socket的建立
    int sockfd = 0;
    sockfd = socket(AF_INET , SOCK_STREAM , 0);

    if (sockfd == -1){
        printf("Fail to create a socket.");
    }

    //socket的連線

    struct sockaddr_in info;
    bzero(&info,sizeof(info));
    info.sin_family = PF_INET;

    //localhost test
    info.sin_addr.s_addr = inet_addr("127.0.0.1");

    info.sin_port = htons(8000);


    int err = connect(sockfd,(struct sockaddr *)&info,sizeof(info));
    if(err==-1){
        printf("Connection error");
    }


    //Send a message to server
    char message[] = {"Hi there"};
    char receiveMessage[100] = {};
    // if(send(sockfd,message,sizeof(message),0)==-1){
    //     printf("send error\n");
    // }
    
    char * arr[3];
    const char * del = ",";
    int cnt = 10;
    while (cnt>0){
        if(recv(sockfd,receiveMessage,sizeof(receiveMessage),0)>0){
            printf("received!\n");
        };
        printf("%s",receiveMessage);
        split_msg(arr,receiveMessage,del);
        printf("%s\n",arr[0]);
        // run();
        send(sockfd,message,sizeof(message),0);
        cnt-=1;
    }
    

    
    printf("close Socket\n");
    close(sockfd);
    return 0;
}
