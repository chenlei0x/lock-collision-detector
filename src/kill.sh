ps -aux | grep python | grep main | awk '{print $2}' | xargs kill
