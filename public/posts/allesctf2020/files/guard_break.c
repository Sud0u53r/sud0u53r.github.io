#include<unistd.h>
#include<sys/wait.h>
#include<sys/prctl.h>
#include<signal.h>
#include<stdlib.h>
#include<string.h>
#include<stdio.h>

unsigned long int solve(char *data) {
	unsigned int out,a,b;
	sscanf(data,"%d + %d",&a,&b);
	return a+b;
}

int main(int argc, char** argv) {
	pid_t pid = 0;
	int inpipefd[2];
	int outpipefd[2];
	char buf[256];
	char msg[256];
	char ans[256];
	char flag[256];
	int status;

	pipe(inpipefd);
	pipe(outpipefd);
	pid = fork();
	if (pid == 0) {
		dup2(outpipefd[0], STDIN_FILENO);
		dup2(inpipefd[1], STDOUT_FILENO);
		dup2(inpipefd[1], STDERR_FILENO);
		prctl(PR_SET_PDEATHSIG, SIGTERM);
		execl("/guard", "/flag.txt", (char*) NULL);
		exit(1);
	}
	close(outpipefd[0]);
	close(inpipefd[1]);

	read(inpipefd[0], buf, 256);
	unsigned long int an = solve(buf);
	sprintf(ans,"%lu",an);
	ans[strlen(ans)]='\n';
	ans[strlen(ans)+1]='\0';
	write(outpipefd[1], ans, strlen(ans));
	read(inpipefd[0], flag, 256);
	printf("Flag: %s\n",flag);
	kill(pid, SIGKILL); //send SIGKILL signal to the child process
	waitpid(pid, &status, 0);
}