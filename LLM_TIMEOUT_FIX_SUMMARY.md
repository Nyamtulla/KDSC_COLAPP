# LLM Timeout Fix Summary

## 🔍 **Problem Identified**
The LLM service was timing out after 180 seconds when parsing receipts, causing the entire parsing process to fail.

## 🛠️ **Solutions Implemented**

### **1. Added Timeout Handling**
- **60-second timeout** for LLM requests (much less than 180s task timeout)
- **Signal-based timeout** using `signal.alarm()` for reliable timeout handling
- **Graceful fallback** when LLM times out

### **2. Optimized LLM Parameters**
```python
options={
    "temperature": 0.1,        # Low temperature for consistent output
    "top_p": 0.9,
    "num_predict": 1024,       # Reduced from 2048 for faster response
    "num_ctx": 2048,          # Limit context window
    "repeat_penalty": 1.1,     # Prevent repetition
    "stop": ["```", "```json", "```\n"]  # Stop at code blocks
}
```

### **3. Simplified System Prompt**
- **Reduced prompt size** by limiting to first 50 categories
- **Shorter, more direct instructions**
- **Faster processing** with concise JSON structure

### **4. Added Fallback Parsing**
- **Regex-based parsing** when LLM times out
- **Simple pattern matching** for common receipt formats
- **Basic product extraction** using price patterns
- **Store name detection** for major retailers

### **5. Increased Task Timeout**
- **300-second job timeout** in RQ worker (up from 180s)
- **Environment variable** `RQ_JOB_TIMEOUT=300`
- **Docker command** updated with `--job-timeout 300`

## 📊 **Performance Improvements**

### **Before:**
- ❌ 180-second timeout causing failures
- ❌ No fallback mechanism
- ❌ Large, verbose system prompts
- ❌ No timeout handling

### **After:**
- ✅ 60-second LLM timeout with fallback
- ✅ Regex fallback parsing
- ✅ Optimized LLM parameters
- ✅ Simplified prompts
- ✅ 300-second task timeout

## 🚀 **Expected Results**

1. **Faster Processing** - LLM responses in under 60 seconds
2. **Higher Success Rate** - Fallback parsing when LLM fails
3. **Better Reliability** - Multiple parsing strategies
4. **Reduced Timeouts** - Proper timeout handling

## 🔧 **Testing**

To test the fixes:

1. **Restart the containers:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. **Upload a receipt** and monitor the logs:
   ```bash
   docker-compose logs -f worker
   ```

3. **Check for timeout messages** in the logs

## 📝 **Log Messages to Look For**

- ✅ `"LLM request completed successfully"`
- ✅ `"Using fallback parsing due to timeout"`
- ✅ `"Fallback parsing completed successfully"`
- ❌ `"Task exceeded maximum timeout value"`

## 🎯 **Next Steps**

1. **Monitor performance** after deployment
2. **Adjust timeout values** if needed
3. **Fine-tune LLM parameters** based on results
4. **Add more fallback patterns** if necessary

The system should now handle receipt parsing much more reliably! 🎉 