// dllmain.cpp : Defines the entry point for the DLL application.
#include <stdio.h>
#include <windows.h> 
#include <iostream>
#include <string>
using namespace std; 
#include "pch.h"
#define _CRT_SECURE_NO_DEPRECATE
#include <NIDAQmx.h>
#include "dllmain.h"

#define DAQmxErrChk(functionCall) if( DAQmxFailed(error=(functionCall)) ) goto Error; else

int32 CVICALLBACK EveryNCallback(TaskHandle taskHandle, int32 everyNsamplesEventType, uInt32 nSamples, void* callbackData);
int32 CVICALLBACK DoneCallback(TaskHandle taskHandle, int32 status, void* callbackData);
void uSleep(int waitTime);
FILE* fp;
LARGE_INTEGER frequency;        // ticks per second
LARGE_INTEGER t1, t2;           // ticks
double elapsedTime;

DataArray* globalArray;
int		*globalHead;
int		*globalTime;
int			localHead = 0;
int			localTime;
int		channelIndex;
int		stopDataCollection = 0;

TaskHandle  globalTaskHandle;

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
#if 1
	AllocConsole();
	FILE* fDummy;
	freopen_s(&fDummy, "CONIN$", "r", stdin);
	freopen_s(&fDummy, "CONOUT$", "w", stderr);
	freopen_s(&fDummy, "CONOUT$", "w", stdout);
#endif
	switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
#if 0
		if (!AllocConsole())
			MessageBox(NULL, L"The console window was not created", NULL, MB_ICONEXCLAMATION);

		FILE* fp;

		freopen_s(&fp, "CONOUT$", "w", stdout);

		printf("Hello console on\n");


		MessageBox(NULL, (L"Pause to see console output."), (L"Pause Here"), MB_OK | MB_SYSTEMMODAL | MB_ICONEXCLAMATION);

		fclose(fp);

		if (!FreeConsole())
			MessageBox(NULL, L"Failed to free the console!", NULL, MB_ICONEXCLAMATION);
#endif
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

void get_NI6255Data(TaskHandle  taskHandle)
{
	int32       error = 0;
//	TaskHandle  taskHandle = 0;
	char        errBuff[2048] = { '\0' };

	BOOL b;
	char msg[1024];
	char ch;
	bool loop = false;

	globalTaskHandle = taskHandle;
	// get ticks per second
	QueryPerformanceFrequency(&frequency);

	// start timer
	QueryPerformanceCounter(&t1);

#if 1
	globalArray = dataArray;
	globalHead = head;
	globalTime = time;
#endif

	FreeConsole();
	AttachConsole(ATTACH_PARENT_PROCESS);
	
	if (!AllocConsole())
		MessageBox(NULL, L"The console window was not created", NULL, MB_ICONEXCLAMATION);

#if 1
	FILE* dummy;

	freopen_s(&dummy, "CONOUT$", "w", stdout);
	freopen_s(&dummy, "CONIN$", "r", stdin);
	freopen_s(&dummy, "CONOUT$", "w", stderr);

#endif
	fopen_s(&fp, "Record.csv", "w");

#if 0
	while (loop == false)
	{

		QueryPerformanceCounter(&t2);

		globalHead[0] = localHead;
		globalTime[0] = (int)((t2.QuadPart - t1.QuadPart) * 1000000.0 / frequency.QuadPart);

		for (channelIndex = 0; channelIndex < BUFFER_SIZE; channelIndex++)
		{
			globalArray->array[localHead][channelIndex] = float(channelIndex);
		}

		localHead = localHead + 1;
		if (localHead > BUFFER_LENGTH - 1)
			localHead = 0;
		globalHead[0] = localHead;

		uSleep(100000);
	}
#if 1
	printf("loop terminated");
#endif




#endif


#if 0	
	/*********************************************/
	// DAQmx Configure Code
	/*********************************************/
	DAQmxErrChk(DAQmxCreateTask("", &taskHandle));
	DAQmxErrChk(DAQmxCreateAIVoltageChan(taskHandle, channelString, "", DAQmx_Val_Diff, -10.0, 10.0, DAQmx_Val_Volts, NULL));
	DAQmxErrChk(DAQmxCfgSampClkTiming(taskHandle, "", samplRate, DAQmx_Val_Rising, DAQmx_Val_ContSamps, 30000));
#endif

	DAQmxErrChk(DAQmxRegisterEveryNSamplesEvent(taskHandle, DAQmx_Val_Acquired_Into_Buffer, 1000, 0, EveryNCallback, NULL));
	DAQmxErrChk(DAQmxRegisterDoneEvent(taskHandle, 0, DoneCallback, NULL));

	/*********************************************/
	// DAQmx Start Code
	/*********************************************/
	DAQmxErrChk(DAQmxStartTask(taskHandle));
	//	gettimeofday(&start, NULL);


	while (stopDataCollection == 0)
	{
		printf("Acquiring samples continuously\r");
	}
#if 0

	printf("\nAcquiring samples continuously. Press Enter to interrupt\n");
	MessageBox(NULL, (L"Pause to see console output."), (L"Pause Here"), MB_OK | MB_SYSTEMMODAL | MB_ICONEXCLAMATION);
//	getchar();
	fclose(fp);
//	FreeConsole();

	printf("End of program, press Enter key to quit\n");
	getchar();
#endif
Error:
	if (DAQmxFailed(error))
		DAQmxGetExtendedErrorInfo(errBuff, 2048);
	if (taskHandle != 0) {
		/*********************************************/
		// DAQmx Stop Code
		/*********************************************/
		printf("\nStop Task");
		DAQmxStopTask(taskHandle);
		DAQmxClearTask(taskHandle);
	}
	if (DAQmxFailed(error))
		printf("DAQmx Error: %s\n", errBuff);

	fclose(fp);
	printf("\nEnd of program");

	return ;


}

void uSleep(int waitTime) {
	__int64 time1 = 0, time2 = 0, freq = 0;

	QueryPerformanceCounter((LARGE_INTEGER*)&time1);
	QueryPerformanceFrequency((LARGE_INTEGER*)&freq);

	do {
		QueryPerformanceCounter((LARGE_INTEGER*)&time2);
	} while (((time2 - time1) * 1000000.0 / freq) < waitTime);
}

int32 CVICALLBACK EveryNCallback(TaskHandle taskHandle, int32 everyNsamplesEventType, uInt32 nSamples, void* callbackData)
{
	int32       error = 0;
	int32		intTime;
	char        errBuff[2048] = { '\0' };
	static int  totalRead = 0;
	int32       read = 0;
	float64     data[30000];
	float64		dataSum = 0;
	int32		bufferTime;

	
	/*********************************************/
	// DAQmx Read Code
	/*********************************************/
//	DAQmxErrChk(DAQmxReadAnalogF64(taskHandle, 1000, 10.0, DAQmx_Val_GroupByScanNumber, data, 3000, &read, NULL));DAQmx_Val_GroupByChannel
	DAQmxErrChk(DAQmxReadAnalogF64(taskHandle, -1, 10.0, DAQmx_Val_GroupByScanNumber, data, 30000, &read, NULL));
	if (read > 0)
	{
		QueryPerformanceCounter(&t2);

		bufferTime = (int)((t2.QuadPart - t1.QuadPart) * 1000000.0 / frequency.QuadPart);

		printf("		Data Size is %d at time %d\r", sizeof(data), bufferTime);

//		printf("%f\r", data[3000]);

#if 0
		globalArray[localHead] = 1.1 * localHead;
		localHead = localHead + 1;
		globalHead[0] = localHead;
		if (localHead >= 20)
			localHead = 0;
#endif

#if 1
		for (int sampleIndex = 0; sampleIndex < 1000; sampleIndex++)
		{
			fprintf(fp, "%d,", bufferTime);
			for (int channelIndex = 0; channelIndex < 28; channelIndex++)
			{
//				dataSum += data[i];
//				printf("%f\r", data[i]);
			//			printf("%f  ", data[i]);
				fprintf(fp, "%f,", data[channelIndex + sampleIndex * 28]);
//				fprintf(fp, "%d,%f,%f,%f\n", intTime + i, data[3 * i], data[3 * i + 1], data[3 * i + 2]);
			}
			fprintf(fp, "\n");
//			printf("Average of %d samples for channel 1 is: %f\r", read, dataSum / read);
		}
#endif
		//		quit = 0;
		fflush(stdout);
	}
Error:
	if (DAQmxFailed(error)) {
		DAQmxGetExtendedErrorInfo(errBuff, 2048);
		/*********************************************/
		// DAQmx Stop Code
		/*********************************************/
		DAQmxStopTask(taskHandle);
		DAQmxClearTask(taskHandle);
		printf("DAQmx Error: %s\n", errBuff);
	}
	return 0;
}

int32 CVICALLBACK DoneCallback(TaskHandle taskHandle, int32 status, void* callbackData)
{
	int32   error = 0;
	char    errBuff[2048] = { '\0' };

	// Check to see if an error stopped the task.
	DAQmxErrChk(status);

Error:
	if (DAQmxFailed(error)) {
		DAQmxGetExtendedErrorInfo(errBuff, 2048);
		DAQmxClearTask(taskHandle);
		printf("DAQmx Error: %s\n", errBuff);
	}
	return 0;
}


void stopLoop()
{
	stopDataCollection = 1;

//	DAQmxStopTask(globalTaskHandle);
//	DAQmxClearTask(globalTaskHandle);
}