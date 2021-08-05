/*********************************************************************
*
* ANSI C Example program:
*    Acq-IntClk.c
*
* Example Category:
*    AI
*
* Description:
*    This example demonstrates how to acquire a finite amount of data
*    using the DAQ device's internal clock.
*
* Instructions for Running:
*    1. Select the physical channel to correspond to where your
*       signal is input on the DAQ device.
*    2. Enter the minimum and maximum voltages.
*    Note: For better accuracy try to match the input range to the
*          expected voltage level of the measured signal.
*    3. Select the number of samples to acquire.
*    4. Set the rate of the acquisition.
*    Note: The rate should be AT LEAST twice as fast as the maximum
*          frequency component of the signal being acquired.
*
* Steps:
*    1. Create a task.
*    2. Create an analog input voltage channel.
*    3. Set the rate for the sample clock. Additionally, define the
*       sample mode to be finite and set the number of samples to be
*       acquired per channel.
*    4. Call the Start function to start the acquisition.
*    5. Read all of the waveform data.
*    6. Call the Clear Task function to clear the task.
*    7. Display an error if any.
*
* I/O Connections Overview:
*    Make sure your signal input terminal matches the Physical
*    Channel I/O Control. For further connection information, refer
*    to your hardware reference manual.
*
*********************************************************************/

#include <time.h>
#include <stdio.h>
#include <windows.h> 
#include <NIDAQmx.h>

#define DAQmxErrChk(functionCall) if( DAQmxFailed(error=(functionCall)) ) goto Error; else

FILE* differentialFile, *singleEndedFile, *configFile;
LARGE_INTEGER frequency;        // ticks per second
LARGE_INTEGER startTime, diffTime, singleTime;           // ticks
double elapsedTime;

#define NI_MAX_CHNL_CNT 40


int main(void)
{
	int32       error=0;
	TaskHandle  diffTaskHandle=0, singleTaskHandle=0;
	int32       read;
	float64     data[1000];
	char        errBuff[2048]={'\0'};
	int			stopLoop = 0;
	int			loopIndex;
	int			channelCount = 28;
	int			scannedObjects;
	int			ch;
	char		niChannel[NI_MAX_CHNL_CNT][10];
	char		channelName[NI_MAX_CHNL_CNT][20];
	float		highRange[NI_MAX_CHNL_CNT];
	float		lowRange[NI_MAX_CHNL_CNT];

	time_t start_time, stop_time, current_time;


//	for (loopIndex = 0, loopIndex < )


	fopen_s(&configFile, "Jupiter_Power_Consumption_PsuedoRealTime_Unit2.csv", "r");

	while (EOF != (ch = getc(configFile)))
		if ('\n' == ch)
			++channelCount;

	rewind(configFile);
//	fopen_s(&configFile, "Jupiter_Power_Consumption_PsuedoRealTime_Unit2.csv", "r");

	for (loopIndex = 0; loopIndex < channelCount; loopIndex++)
	{
		scannedObjects = fscanf(configFile, "%s, %s, %f, %f\n", niChannel[loopIndex], channelName[loopIndex], &highRange[loopIndex], &lowRange[loopIndex]);
		printf("Num Scanned: %d", scannedObjects);
	}

	for (loopIndex = 0; loopIndex < channelCount; loopIndex++)
	{
		printf("%s, %s, %f, %f\n", niChannel[loopIndex], channelName[loopIndex], highRange[loopIndex], lowRange[loopIndex]);
	}


	printf("End of program, press Enter key to quit\n");
	getchar();
	return 0;
//	while (stopLoop == 0)
//	{
//		fscanf(configFile, "%s, %s, %f, %f", channel, channelName, highRange, lowRange)
//	}


	fopen_s(&differentialFile, "differentialData.csv", "a");
	fopen_s(&singleEndedFile, "singleEndedData.csv", "a");

	/*********************************************/
	// DAQmx Configure Code
	/*********************************************/
		DAQmxErrChk(DAQmxCreateTask("", &diffTaskHandle));
		DAQmxErrChk(DAQmxCreateTask("", &singleTaskHandle));
		DAQmxErrChk(DAQmxCreateAIVoltageChan(diffTaskHandle, "Dev1/ai50", "", DAQmx_Val_Diff, -10.0, 10.0, DAQmx_Val_Volts, NULL));
		DAQmxErrChk(DAQmxCreateAIVoltageChan(singleTaskHandle, "Dev1/ai50", "", DAQmx_Val_RSE, -10.0, 10.0, DAQmx_Val_Volts, NULL));
		DAQmxErrChk(DAQmxCfgSampClkTiming(diffTaskHandle, "", 1000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 2));
		DAQmxErrChk(DAQmxCfgSampClkTiming(singleTaskHandle, "", 1000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 2));
//		DAQmxErrChk(DAQmxCfgImplicitTiming(diffTaskHandle, DAQmx_Val_FiniteSamps, 1));
//		DAQmxErrChk(DAQmxCfgImplicitTiming(singleTaskHandle, DAQmx_Val_FiniteSamps, 1));

		// get ticks per second
		QueryPerformanceFrequency(&frequency);

#if 0
		start_time = time(NULL);
		// start timer
		QueryPerformanceCounter(&startTime);
		while (stopLoop == 0)
		{
			DAQmxErrChk(DAQmxStartTask(diffTaskHandle));
			DAQmxErrChk(DAQmxReadAnalogF64(diffTaskHandle, 1, 10.0, DAQmx_Val_GroupByChannel, data, 1, &read, NULL));
			DAQmxErrChk(DAQmxStopTask(diffTaskHandle));

			QueryPerformanceCounter(&diffTime);
			elapsedTime = (int)((diffTime.QuadPart - startTime.QuadPart) * 1000000.0 / frequency.QuadPart);

			fprintf(differentialFile, "%d, %f\n", (int)elapsedTime, data[0]+data[1]);

			DAQmxErrChk(DAQmxStartTask(singleTaskHandle));
			DAQmxErrChk(DAQmxReadAnalogF64(singleTaskHandle, 2, 10.0, DAQmx_Val_GroupByChannel, data, 2, &read, NULL));
			DAQmxErrChk(DAQmxStopTask(singleTaskHandle));

			QueryPerformanceCounter(&singleTime);
			elapsedTime = (int)((singleTime.QuadPart - startTime.QuadPart) * 1000000.0 / frequency.QuadPart);

			fprintf(singleEndedFile, "%d, %f\n", (int)elapsedTime, data);

			current_time = time(NULL);
			if (current_time >= start_time + 1 * 60)
			{
				stopLoop = 1;
			}
		}
		stop_time = time(NULL);
#endif
		printf("Loop Finished. Elapsed Time in Seconds: %d", (int)(stop_time - start_time));

		return 0;
		

	printf("Acquired %d points\n",(int)read);

Error:
	if( DAQmxFailed(error) )
		DAQmxGetExtendedErrorInfo(errBuff,2048);
	if(singleTaskHandle !=0 )  {
		/*********************************************/
		// DAQmx Stop Code
		/*********************************************/
		DAQmxStopTask(singleTaskHandle);
		DAQmxClearTask(singleTaskHandle);
	}
	if( DAQmxFailed(error) )
		printf("DAQmx Error: %s\n",errBuff);
	printf("End of program, press Enter key to quit\n");
	getchar();
	return 0;
}
