#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include <excpt.h>
#include <winerror.h>
#include "beacon_funcs.h"

/* Helper functions */

char empty_string[2] = "\x00\x00";

// Handle exceptions so we don't crash our calling app. 
// This is perhaps a little bit ott
LONG WINAPI VectoredExceptionHandler(struct _EXCEPTION_POINTERS *ExceptionInfo) {
	LPTSTR errorText = NULL;
	MSVCRT$printf("\n EXCEPTION \n --------- \n ");
	HMODULE hNtDll = KERNEL32$LoadLibraryA("NTDLL.DLL");
	if (hNtDll != NULL) {

		DWORD msg_len = FormatMessage(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_HMODULE, hNtDll, NTDLL$RtlNtStatusToDosError(ExceptionInfo->ExceptionRecord->ExceptionCode), MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPTSTR)&errorText, 0, NULL);
		if (errorText != NULL) {
		MSVCRT$printf("Exception while running object file: %s @ %p [0x%X]\n --------- \n\n", errorText, ExceptionInfo->ExceptionRecord->ExceptionAddress, ExceptionInfo->ExceptionRecord->ExceptionCode);
		}

	} else {

		MSVCRT$printf("Exception while running object file: \n @ %p [0x%X]\n --------- \n\n", ExceptionInfo->ExceptionRecord->ExceptionAddress, ExceptionInfo->ExceptionRecord->ExceptionCode);
	}
	//KERNEL32$ExitThread(-1);
	//. Changed to terminate thread as was having issues with exit thread trying to free heap allocations, which was fine, except when the exception is a heap corruption..
	KERNEL32$TerminateThread(thread_handle, -1);
}


void debugPrintf(char *fmt, ...) {
	va_list argp;

	if (global_debug_flag) {
		va_start(argp, fmt);
		MSVCRT$vprintf(fmt, argp);
		va_end(argp);
	}
}

// we have a wrapper around our go function to change our globals into parameters
// because we can't pass args in a usual way to the new thread
// We can also do some housekeeping/setup here
void go_wrapper() {
	void *exception_handler = KERNEL32$AddVectoredExceptionHandler(0, VectoredExceptionHandler);
	debugPrintf("[*] --- UNMANAGED CODE START --- \n");
	debugPrintf("[*] --- Calling BOF go() function --- \n");
	
	//thread_handle = KERNEL32$GetCurrentThread();

	// setup our output buffer
	// global_buffer should have already been allocated by the loader
	global_buffer_cursor = global_buffer;
	global_buffer_remaining = global_buffer_len;

	go(argument_buffer, argument_buffer_length);
	debugPrintf("[*] BOF finished\n");
	// TEST CODE TO CAUSE A CRASH
	/*
	while (1) {
	HANDLE process_heap = KERNEL32$GetProcessHeap();
		MSVCRT$printf("CRASH!\n");
	global_buffer = KERNEL32$HeapReAlloc(process_heap, HEAP_ZERO_MEMORY, global_buffer - 100,  global_buffer_len +1000);


	char *ptr = 0;

	*ptr = 0;
	}*/
	debugPrintf("[*] UNMANAGED CODE END\n");
	KERNEL32$RemoveVectoredExceptionHandler(exception_handler);
	KERNEL32$ExitThread(0);
	
}


void ReallocOutputBuffer(size_t increment_size) {
	HANDLE process_heap = KERNEL32$GetProcessHeap();
	increment_size = increment_size + 1024;
	debugPrintf("[*] Reallocating global output buffer to new size %d\n", global_buffer_len + increment_size);

	size_t cursor_offset = global_buffer_cursor - global_buffer;

	global_buffer = KERNEL32$HeapReAlloc(process_heap, HEAP_ZERO_MEMORY, global_buffer,  global_buffer_len + increment_size);

	if (global_buffer == NULL) {
		MSVCRT$printf("[!!] Unable to realloc output buffer - exiting BOF\n");
		KERNEL32$ExitThread(-1);
	}

	global_buffer_cursor = global_buffer + cursor_offset;
	global_buffer_len += increment_size;
	global_buffer_remaining += increment_size;
}

// Output functions

// Instead of printing to the console, this saves the fomatted string into the global buffer
void BeaconPrintf(int type, char *fmt, ...) {
        va_list argp;
        va_start(argp, fmt);

	char callback_output[] = "\n[ ] CALLBACK_OUTPUT:\t";
	char callback_output_oem[] = "\n[ ] CALLBACK_OUTPUT_OEM:\t";
	char callback_error[] = "\n[!] CALLBACK_ERROR:\t";
	char callback_output_utf8[] = "\n[ ] CALLBACK_OUTPUT_UTF8:\t";
	char callback_output_unknown[] = "\n[!] UNKNOWN TYPE:\t";

	char *callback_type_text;


        switch (type) {
                // from beacon.h
                case 0x0:
			callback_type_text = callback_output;
                        break;
                case 0x1e:
			callback_type_text = callback_output_oem;
                        break;
                case 0x0d:
			callback_type_text = callback_error;
                        break;
                case 0x20:
			callback_type_text = callback_output_utf8;
                        break;
                default:
			callback_type_text = callback_output_unknown;
			debugPrintf("[!] Unknown callback type %d supplied in BeaconPrintf\n", type);
                        break;
        }


	// Check length and realloc here
	if ((MSVCRT$strlen(callback_type_text) + MSVCRT$vsnprintf(NULL, 0, fmt, argp)) > global_buffer_remaining) {
		ReallocOutputBuffer(MSVCRT$strlen(callback_type_text) + MSVCRT$vsnprintf(NULL, 0, fmt, argp));
	}


	size_t written = 0;

	written = MSVCRT$_snprintf(global_buffer_cursor, global_buffer_remaining, callback_type_text);
	if (written <0) {
		MSVCRT$printf("[!] Error copying type text in BeaconPrintf\n");
		return;
	}
	global_buffer_cursor += written;
	global_buffer_remaining -= written;

	written = MSVCRT$vsnprintf(global_buffer_cursor, global_buffer_len, fmt, argp);
	if (written <0) {
		MSVCRT$printf("[!] Error copying message text in BeaconPrintf\n");
		return;
	}
	global_buffer_cursor += written;
	global_buffer_remaining -= written;


        va_end(argp);
	return;
};

void BeaconOutput(int type, char *data, int len) {
	debugPrintf("in BeaconOutput - received %d bytes\n", len);
	//hexdump(data, len);
	// check we have space in out output buffer
	if (len > global_buffer_remaining) {
		ReallocOutputBuffer(len);
	}
	MSVCRT$memcpy(global_buffer_cursor, data, len);
	global_buffer_cursor += len;
	global_buffer_remaining -= len;
}

void hexdump(char * buffer, int len) {
	if (global_debug_flag) {
		MSVCRT$printf("--\n");
		for (int i =0 ; i< len; i++) {
			MSVCRT$printf("%02x ", buffer[i]);
		}
		MSVCRT$printf("--\n");
	}
}

// Data API

void BeaconDataParse (datap * parser, char * buffer, int size) {
	debugPrintf("[*] Initialising DataParser...global arg length: %d, local length: %d\n", argument_buffer_length, size);

	// we want to set our parser fields to point to the right stuff...
	parser->original = buffer; // The original buffer
	parser->buffer = buffer; // current pointer into our buffer
	parser->length = size; // remaining length of data
	parser->size = size; // total size of the buffer

	hexdump(buffer, size);
	hexdump(parser->buffer, size);

	debugPrintf("[*] Finished initialising DataParser\n");
}

int BeaconDataLength (datap *parser) {
	return parser->length;
}

char * BeaconDataExtract (datap *parser, int * size) {

	empty_string[0] = '\x00'; // We need to explicitly init this here, as it gets put in the BSS which our loader doesn't set to zero
	empty_string[1] = '\x00'; // Set two bytes beacuse some BOF clients might treat this as a wchar
	debugPrintf("[*] BeaconDataExtract...%d / %d bytes read\n", parser->size - parser->length, parser->size);

	// check we have enough space left in our buffer - need at least space for the type and the length
	if (parser->length > 2 * sizeof(uint32_t)) {
		// read a UINT from our current data buffer position to give us the type
		uint32_t arg_type = *(uint32_t *)parser->buffer;
		if (arg_type == BINARY) {
			// we need to increment the buffer pointer only if we're in the right type
			parser->buffer = parser->buffer + sizeof(uint32_t);
			uint32_t arg_len = *(uint32_t *)parser->buffer;
			debugPrintf("[*] Have a binary variable (type %d) of length %d\n", arg_type, arg_len);
			// check have enough space left in our buffer
			if (parser->length - 2*sizeof(uint32_t) >= arg_len) {
				// we have a choice here, we can either return a pointer to the data in the buffer
				// or allocate some more memory, and point back at that. 
				// I'm not too sure what cobalt does, so just returning ptr to buffer!
				parser->buffer = parser->buffer + sizeof(uint32_t);

				if (size != NULL) *size = arg_len;

				char *return_ptr = parser->buffer;
				hexdump(return_ptr, arg_len);
				parser->buffer = parser->buffer + arg_len;
				parser->length = parser->length - (arg_len + 2*sizeof(uint32_t));
				debugPrintf("[*] Returning %d byte 'binary' value\n", arg_len);
				return return_ptr;
			} else {
				debugPrintf("[!] Unable to extract binary data - buffer len: %d \n", parser->length);
				if (size != NULL) *size = 1;
				return empty_string;
			}
		} else {
			debugPrintf("[!] Unable to extract binary data - wrong type: %d \n", arg_type);
			if (size != NULL) *size = 1;
			return empty_string;

		}
	} 

	debugPrintf("[!] Unable to extract binary data - length too short: %d\n", parser->length);
	if (size != NULL) *size = 1;
	return empty_string;
}

int32_t BeaconDataInt(datap *parser) {
	debugPrintf("[*] BeaconDataInt...%d / %d bytes read\n", parser->size - parser->length, parser->size);

	if (parser->length >= 3 * sizeof(uint32_t)) {

		uint32_t arg_type = *(uint32_t *)parser->buffer;
		if (arg_type == INT_32) {
			// we need to increment the buffer pointer only if we're in the right type
			parser->buffer = parser->buffer + sizeof(uint32_t);
			// check the length
			uint32_t arg_len = *(uint32_t *)parser->buffer;
			parser->buffer = parser->buffer + sizeof(uint32_t);

			if (arg_len != sizeof(uint32_t)) {
				// TODO - rewind the buffer pointer? things have gone badly wrong anyway and we'll probably crash??
				return 0;
			}

			uint32_t arg_data = *(uint32_t *)parser->buffer;
			parser->buffer = parser->buffer + sizeof(uint32_t);
			parser->length = parser->length - (3 * sizeof(uint32_t));
			debugPrintf("[*] Returning %d\n", arg_data);
			return arg_data;
		} else {
			debugPrintf("[!] Asked for 4-byte integer, but have type %d, returning 0\n", arg_type);
			return 0;
		}
	} 

	debugPrintf("[!] Asked for int, but not enough left in our buffer so returning 0\n");

	return 0;
}

int16_t BeaconDataShort(datap *parser) {
	debugPrintf("[*] BeaconDataShort...%d / %d bytes read\n", parser->size - parser->length, parser->size);

	if (parser->length >= (2*sizeof(uint32_t) + sizeof(uint16_t))) {
		uint32_t arg_type = *(uint32_t *)parser->buffer;
		if (arg_type == INT_16) {
			// we need to increment the buffer pointer only if we're in the right type
			parser->buffer = parser->buffer + sizeof(uint32_t);
			// check the length
			uint32_t arg_len = *(uint32_t *)parser->buffer;
			parser->buffer = parser->buffer + sizeof(uint32_t);

			if (arg_len != sizeof(uint16_t)) {
				// TODO - rewind the buffer pointer? things have gone badly wrong anyway and we'll probably crash??
				return 0;
			}

			uint16_t arg_data = *(uint16_t *)parser->buffer;
			parser->buffer = parser->buffer + sizeof(uint16_t);
			parser->length = parser->length - (2*sizeof(uint32_t) + sizeof(uint16_t));
			debugPrintf("[*] Returning %d\n", arg_data);
			return arg_data;
		} else {
			debugPrintf("[!] Asked for 2-byte integer, but have type %d, returning 0\n", arg_type);
			return 0;
		}
	}
	debugPrintf("[!] Asked for short, but not enough left in our buffer so returning 0\n");

	return 0;
}

// Format API

// internal helper function
void _reallocFormatBuffer(formatp * format, int increment) {
	int current_offset = format->size - format->length;
	format->original = MSVCRT$realloc(format->original, increment + format->size);

	if (format->original == NULL) {
		MSVCRT$puts("[!] Error reallocating format buffer \n");
		return;
	}

	format->buffer = format->original + current_offset;

	format->size = format->size + increment;
	format->length += increment;

}

void BeaconFormatAlloc(formatp * format, int maxsz) {
	format->original = MSVCRT$calloc(maxsz, 1);
	format->buffer = format->original;
	format->length = 0;
	format->size = maxsz;
}

void BeaconFormatReset(formatp * format) {
	format->length = 0;
	format->buffer = format->original;
}

void BeaconFormatFree(formatp * format) {
	MSVCRT$free(format->original);
	// I'm not too sure if should set these or not - but this seems safer
	format->buffer = NULL;
	format->length = 0;
	format->size = 0;
	return;
}

void BeaconFormatAppend(formatp * format, char * text, int len) {
	int increment;
	if (len >= format->length) {
		// realloc to make space
		// Our smalled realloc is 1024
		if (len - format->length < 1024) {
			increment = 1024;
		} else {
			increment = len + 1024;
		}
		_reallocFormatBuffer(format, increment);
	}

	MSVCRT$memcpy(format->buffer, text, len);
	return;
}

void BeaconFormatPrintf(formatp * format, char * fmt, ... ) {
	va_list argp;
	size_t required_size = MSVCRT$vsnprintf(NULL, 0, fmt, argp);
	if (required_size < format->length) {
		_reallocFormatBuffer(format, required_size + 1024);
	}
	MSVCRT$vsnprintf(format->buffer, format->length, fmt, argp);
	return;
}

char * BeaconFormatToString(formatp *format, int * size) {
	// TODO is this really right? or is there some processing

	*size = MSVCRT$strlen(format->original);

	return format->original;
}

void BeaconFormatInt(formatp *format, int value) {
	size_t required_size = MSVCRT$_snprintf(NULL, 0, "%d", value);
	if (required_size < format->length) {
		_reallocFormatBuffer(format, required_size + 1024);
	}
	MSVCRT$_snprintf(format->buffer, format->length, "%d", value);
	return;
}


// Token Functions
// not sure if/how to implement these
BOOL BeaconUseToken(HANDLE token) {
	MSVCRT$puts("[!] BeaconUseToken is unimplemented - ignoring request\n");
	return FALSE;
}

void BeaconRevertToken() {
	MSVCRT$puts("[!] BeaconRevertToken is unimplemented - ignoring request\n");
	return;
}

BOOL BeaconIsAdmin() {
	MSVCRT$puts("[!] BeaconIsAdmin is unimplemented - ignoring request\n");
	return FALSE;
}

// Utility Functions
BOOL toWideChar(char *src, wchar_t *dst, int max) {
	if (src == NULL || dst == NULL) return FALSE;
	// max is given *in bytes*, so divide by two to get max for MBTWC
	KERNEL32$MultiByteToWideChar(CP_ACP, 0, src, -1, dst, max / 2);

}
