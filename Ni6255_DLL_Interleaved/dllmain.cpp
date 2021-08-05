// dllmain.cpp : Defines the entry point for the DLL application.
#include <stdio.h>
#include <windows.h> 
#include <iostream>
//#include <string>
using namespace std; 
#include "pch.h"
#define _CRT_SECURE_NO_DEPRECATE
#include <NIDAQmx.h>
#include "dllmain.h"

#define DAQmxErrChk(functionCall) if( DAQmxFailed(error=(functionCall)) ) goto Error; else

//int32 CVICALLBACK EveryNCallback(TaskHandle taskHandle, int32 everyNsamplesEventType, uInt32 nSamples, void* callbackData);
//int32 CVICALLBACK DoneCallback(TaskHandle taskHandle, int32 status, void* callbackData);

void uSleep(int waitTime);
static FILE* fpDiff, *fpSingle;
LARGE_INTEGER frequency;        // ticks per second
LARGE_INTEGER t1, t2;           // ticks
double elapsedTime;



static int		loadCount = 0;
char diffFileName[] = "diffFile.csv";
char singleFileName[] = "singleFile.csv";

int		stopDataCollection = 0;

TaskHandle  globalTaskHandle;

BOOL APIENTRY DllMain( HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
		loadCount = 1;
#if 1
		FreeConsole();
		AttachConsole(ATTACH_PARENT_PROCESS);

		if (!AllocConsole())
			MessageBox(NULL, L"The console window was not created", NULL, MB_ICONEXCLAMATION);

		FILE* dummy;

		freopen_s(&dummy, "CONOUT$", "w", stdout);
		freopen_s(&dummy, "CONIN$", "r", stdin);
		freopen_s(&dummy, "CONOUT$", "w", stderr);
#endif
//		printf("\nWe got to DllMain, Load Count %d\n", loadCount);

		fopen_s(&fpDiff, "diffFile.csv", "w");
		fopen_s(&fpSingle, "singleFile.csv", "w");

    case DLL_THREAD_ATTACH:
		loadCount += 1;
		//I think we come here every time the DLL is called from python
//		printf("\nWe got to DllMain, Load Count %d\n", loadCount);
	case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

//The tasks are set up in the python code. One task is set up as a differential measurement
//and the other is set up as single ended. Each task has all the channels assigned that are listed
//in the configuration file Jupiter_Power_Consumption_SheetOnly_Unit2.xlsx
void get_NI6255Data_Interleaved(TaskHandle  taskHandle1, TaskHandle  taskHandle2, int channelCount)
{
	int32       error = 0;
	char        errBuff[2048] = { '\0' };
	int32       read = 0;
	float64     data[100000];
	float64		diffData, singleData;
	float64		diffSum, singleSum;
	int32		bufferTime, sampleIndex, channelIndex;

	// get ticks per second
	QueryPerformanceFrequency(&frequency);

	// start timer
	QueryPerformanceCounter(&t1);

	while (stopDataCollection == 0)
	{
		//We will start and stop each task sequentially. That way the differential and single ended measurements
		//are as close in time as possible. We only get one sample per channel. These tasks are set up in python
		//as continuous acquisitions but don't need to be. That functionality is not useful when we start and stop 
		//the tasks between each acquisition.
		DAQmxStartTask(taskHandle1);
		//Experimentation seems to indicate that a choice of 1 for numSampsPerChan the second parameter results in an imediate return of data. 
		//Choosing 2 causes it to return as expected with a delay time related to the sample rate??? This is not documented in the NI DAQmx help.
		//The other thing that is still mysterious is that it appears to only take one sample time to get two samples.
		//Perhaps one sample is ready immediately then we only have to wait for the second sample? That might agree with how one sample seems to return immediately as mentioned above.
		//The first sample appears to be valid. So far there doesn't seem to be any major concern here but for sure we want the rate at which data is captured
		//to be throttled by the sample rate and not the speed code runs so for now let's do this two samples and average them thing I have here.
		DAQmxErrChk(DAQmxReadAnalogF64(taskHandle1, 100, 10, DAQmx_Val_GroupByChannel, data, 100000, &read, NULL));
		if (read > 0)
		{
			QueryPerformanceCounter(&t2);

			bufferTime = (int)((t2.QuadPart - t1.QuadPart) * 1000000.0 / frequency.QuadPart);

			fprintf(fpDiff, "%d,", bufferTime);
			for (channelIndex = 0; channelIndex < channelCount; channelIndex++)
			{
				diffSum = 0.0;
				for (sampleIndex = 0; sampleIndex < read; sampleIndex++)
				{
					diffSum += data[channelIndex * read + sampleIndex];
				}
				diffData = diffSum / read;
				fprintf(fpDiff, "%f,", diffData);
			}
			fprintf(fpDiff, "\n");
		}
		DAQmxStopTask(taskHandle1);
//		uSleep(1000);
#if 1
		DAQmxStartTask(taskHandle2);
		DAQmxErrChk(DAQmxReadAnalogF64(taskHandle2, 100, 10, DAQmx_Val_GroupByChannel, data, 100000, &read, NULL));
		if (read > 0)
		{
			QueryPerformanceCounter(&t2);

			bufferTime = (int)((t2.QuadPart - t1.QuadPart) * 1000000.0 / frequency.QuadPart);

			fprintf(fpSingle, "%d,", bufferTime);
			for (channelIndex = 0; channelIndex < channelCount; channelIndex++)
			{
				singleSum = 0.0;
				for (sampleIndex = 0; sampleIndex < read; sampleIndex++)
				{
					singleSum += data[channelIndex * read + sampleIndex];
				}
				singleData = singleSum / read;
				fprintf(fpSingle, "%f,", singleData);
			}
			fprintf(fpSingle, "\n");
		}
		DAQmxStopTask(taskHandle2);
#endif
	}

	fclose(fpDiff);
	fclose(fpSingle);
//	FreeConsole();
//	PostQuitMessage(0);
Error:
	if (DAQmxFailed(error)) {
		DAQmxGetExtendedErrorInfo(errBuff, 2048);
		/*********************************************/
		// DAQmx Stop Code
		/*********************************************/
		DAQmxStopTask(taskHandle1);
		DAQmxClearTask(taskHandle1);
		DAQmxStopTask(taskHandle2);
		DAQmxClearTask(taskHandle2);
		printf("DAQmx Error: %s\n", errBuff);
	}
	return;
}

void uSleep(int waitTime) {
	__int64 time1 = 0, time2 = 0, freq = 0;

	QueryPerformanceCounter((LARGE_INTEGER*)&time1);
	QueryPerformanceFrequency((LARGE_INTEGER*)&freq);

	do {
		QueryPerformanceCounter((LARGE_INTEGER*)&time2);
	} while (((time2 - time1) * 1000000.0 / freq) < waitTime);
}

void stopLoop()
{
	stopDataCollection = 1;
	printf("Stop Data Loop");
}