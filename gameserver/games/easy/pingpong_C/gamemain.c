#include <math.h>
#include <stdio.h>
#include <stdlib.h>
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
void play(){
  return;
}
void game(){
  
  play();
  return;
}
int main(){
  init();
  game();
  return 0;

}
