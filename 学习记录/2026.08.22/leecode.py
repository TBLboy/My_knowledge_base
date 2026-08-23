### 哈希表

# 两数之和
class solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, num in enumerate(nums):
            number = target - num
            if number in seen:
                return [i,seen[number]]
            seen[num] = i
# 思路总结：遍历列表中每一个数字，然后计算出目标数字，目标数字的值就是判断的特征。判断改特征是不是在字典里，如果在，就直接返回i以及这个特征对应的value，如果
# 如果不在，那就把当前的数字作为特征加入字典中


# 字母异分为词
class Solution:
    def groupAnagrams(self, strs):
        group = {}
        for s in strs:
            key = tuple(sorted(s))  # 对字符串进行排序，需要注意字符串没有.sort方法，排序后转换成元组才能作为key，list没办法作为key
            group.setdefault(key,[]).append(s)
        return list(group.values) # 注意了，字典.keys()和.values()都是方法，要加括号
# 思路总结：遍历列表中的每一个字符，首先排序（调用sorted()方法），然后转换成元组（排序后返回的列表不能作为key），这个就是判断的特征，然后调用字典的setdefault()
# 方法，有这个特征就返回这个特征的value，没有就创建这个特征和指定的value对象。有的话返回value然后把当前的字符创append进去。遍历循环结束之后就返回list(字典.values())


# 最长序列
class Solution:
    def longestConsecutive(self, nums):
        longest = 0
        nums_set = set(nums) # 把列表转换成集合，这样可以去除重复
        for num in nums_set:
            if num - 1 not in nums_set:  # 说明这个数字是一个序列的起点
                current = num
                length = 1
                while current + 1 in nums_set: # 说明下一个数字存在
                    current += 1
                    length += 1
                longest = max(longest, length)
        return longest
# 思路解析：最长序列，首先明白重复的数字不能增加序列长度，于是把列表转换成集合，去除重复。接着遍历集合中的每一个元素。如果这个元素-1不在这个集合，那么这个就是一个序列的起点
# 从起点开始，进入while循环，判断现在这个数字+1还在不在集合中。在的话就长度+1,现在的数值+1.
# 每一次while循环之后就更新一下Longest，最终就能找到最长的序列长度

# 哈希表

# 双指针

# 移动0/非零元素
class Solution:
    def moveZeros(self, nums):
        slow = 0
        for fast in range(len(nums)):
            if nums[fast] != 0:
                nums[slow], nums[fast] = nums[fast], nums[slow]
                slow +=1
        return nums
# 思路梳理：这个题目看似很复杂，其实思路很简单，数组里只有两种数字，0和非零。并且这个要求直接修改列表本身，非零数字按照原本数字移动到列表头部。那么要做的事情就很简单，只需要创建
# 两个指针，一个是慢指针，一个快指针。快指针遍历整个数组，寻找非0元素，慢指针代表要把这个元素移动到哪里。因为快指针遍历的顺序本身就和非零元素出现的顺序是一样的，因此移动非零元素之后
# 非两元素在开头出现的顺序也是一样的。

# 盛最多水的容器
class Solution:
    def maxArea(self, nums):
        left = 0
        right = len(nums) - 1
        maxarea = 0
        while left < right:
            area = (right - left) * min(nums[left], nums[right])
            maxarea = max(maxarea, area)
            if nums[left] < nums[right]:
                left += 1
            else:
                right -= 1
        return maxarea
# 题目解析：经典的左有双指针题目。开局先左边一个指针右边一个指针，然后计算当前的面积，并且max一下。然后判断，如果左边高度比较低，那么就向右移动左侧指针。反之就向左移动右边的指针
# 如果两侧高度一样，那么就随便移动其他的指针。至于为什么这种哪边小就移动哪个，为什么两边同样高随便移动，不需要考虑那么多

# 三数之和 #这个很难多看看 ***
class Solution:
    def threeSum(self, nums):
        answer = []
        nums.sort()
        for i in range(len(nums)-2):
            if i>0 and nums[i] == nums[i-1]:
                continue
            if nums[i]>0:
                break
            left, right = i+1, len(nums)-1
            while left<right:
                total = nums[i]+nums[left]+nums[right]
                if total == 0:
                    answer.append([nums[i],nums[left],nums[right]])
                    left+=1
                    right-=1
                    while left<right and nums[left] == nums[left-1]:
                        left+=1
                    while left<right and right!=len(nums)-1 and nums[right] == nums[right+1]:
                        right -=1
                elif total < 0:
                    left +=1 
                else:
                    right -= 1
        return answer

# 无重复字符的最长子串 ******
class  Solution:
    def lengthOfLongestSubstring(self, s):
        """
        怎么这么难？？？
        滑动窗口，创建一个字典记录每个字符最后出现的位置，如果这个字符串出现过，并且上一次出现的位置是在窗口内，就从这个字符处截断
        if里面只做截断，不做位置更新
        """
        last = {}
        answer = 0
        left = 0
        for right, char in enumerate(s):
            if char in last and last[char] >= left:
                left = last[char]+1
            last[char] = right
            answer = max(answer, right-left+1)
        return answer

# 找到字符串中所有字母异位词********（注意这个from collections import Counter）

class Solution:
    def findAnagrams(self, s, p):
        from collections import Counter
        if len(p)>len(s):
            return []
        feature = Counter(p)
        window = Counter(s[:len(p)])
        answer = []
        if window == feature:
            answer.append(0)
        for right in range(len(p),len(s)):
            window[s[right]]+=1
            left = right - len(p)
            left_char = s[left]
            window[left_char] -= 1
            if window[left_char] == 0:
                del window[left_char]
            if window == feature:
                answer.append(right-len(p)+1)
        return answer
# 思路解析：这里使用了一个特殊的计数字典Counter，这个字典的特点就是，输入一个列表，只要列表中的元素本身可以哈希，那么就可以统计每个元素出现的次数。并且访问不存在的元素的时候，会直接返回0
# 这样就可以先把p转换成一个Counter，然后使用固定长度的滑动窗口，每次滑动都把新出现的字母在Counter中的数量+1,离开窗口的字母数量-1.然后判断窗口counter和feature是否想等。相等就把窗口的开头的
# 序号添加到结果里即可

# 双指针

# 子串

# 和为k的子数组**************************
class Solution:
    def subarraySum(self, nums, k):
        """
        这个题目和寻找数组里两个数字和等于目标值的题目很像。定义一个前缀和，代表从当前位置开始，后边的数字和当前数字之和。
        然后创建一个hashmap，我们寻找的思路就是，遍历整个数组，对于当前位置的前缀和，根据要求的k，寻找一个目标前缀和。
        然后hashmap中存放的特征值是前缀和，值就是这个前缀和有多少个对应的数组
        这样可以根据当前位置得到一个target，只需要把hashmap中这个target对应的值拿出来，加到answer上就行
        然后更新hash中这个特征只对应的值
        """
        prefix_count = {0: 1}
        prefix_sum = 0
        answer = 0
        for num in nums:
            prefix_sum+=num
            target = prefix_sum-k
            answer = answer+prefix_count.get(target,0)
            if prefix_sum in prefix_count:
                prefix_count[prefix_sum]+=1
            else:
                prefix_count[prefix_sum]=1
        return answer

# 子串

# 普通数组

# 最大子数组和：**************
class Solution(object):
    def maxSubArray(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        仔细想想为什么这么写？为什么current和num比大小？
        """
        current = answer = nums[0]
        for num in nums[1:]:
            current = max(num, current + num)
            answer =max(answer, current)
        return answer

# 普通数足






# 动态规划

# 爬楼梯
class Solution(object):
    def climbStairs(self, n):
        """
        :type n: int
        :rtype: int
        使用飞播拿起数列，i的数值等于i-1与i-2的数值和
        """
        first = second = 1
        for _ in range(n):
            first, second = second, first + second
        return first

# 养会三角形
class Solution(object):
    def generate(self, numRows):
        """
        :type numRows: int
        :rtype: List[List[int]]
        这里有一个细节要注意，第二层循环，在row_index=0和1的时候分别是range(0,1)和range(1,1)，这两个其实都是不会执行的循环，这样可以自动跳过一些无效的场景
        """
        trangle = []

        for row_index in range(numRows):
            row = [1]*(row_index + 1)
            for j in range(1,row_index):
                row[j] = trangle[row_index-1][j-1]+trangle[row_index-1][j]
            trangle.append(row)
        return trangle

# 打家劫舍
class Solution(object):
    def rob(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        dp[i]=max(dp[i-1],dp[i-2]+money)
        """
        previous_one = 0
        previous_two = 0
        current =0

        for money in nums:
            current = max(previous_one, previous_two+money)
            previous_two = previous_one
            previous_one = current
        return current

# 完全平方数
class Solution(object):
    def numSquares(self, n):
        """
        :type n: int
        :rtype: int
        背下来吧
        """
        dp = [0] + [float("inf")]*n
        for value in range(1, n+1):
            square = 1
            while square*square <= value:
                dp[value] = min(
                    dp[value],
                    dp[value - square*square] + 1
                )
                square += 1
        return dp[n]

# 零钱兑换
class Solution(object):
    def coinChange(self, coins, amount):
        """
        :type coins: List[int]
        :type amount: int
        :rtype: int
        多看看多学学，使用min或者max包住递推公式来
        """
        dp = [0] + [float("inf")]*amount

        for value in range(1, amount+1):
            for coin in coins:
                if coin <= value:
                    dp[value] = min(
                        dp[value],
                        dp[value - coin] + 1
                    )
        if dp[amount] == float("inf"):
            return -1
        return dp[amount]

# 单词拆分
class Solution(object):
    def wordBreak(self, s, wordDict):
        """
        :type s: str
        :type wordDict: List[str]
        :rtype: bool
        谁发明的傻逼切片？？？？
        """
        word = set(wordDict)

        dp = [False]*(len(s) + 1)
        dp[0] = True
        for end in range(1, len(s) + 1):
            for start in range(end):
                if dp[start] and s[start:end] in word:
                    dp[end] = True
        return dp[end]


# 最长递增子序列
class Solution(object):
    def lengthOfLIS(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        这里使用了贪心算法
        """
        from bisect import bisect_left
        tail = []
        for num in nums:
            index = bisect_left(tail, num)
            if index == len(tail):
                tail.append(num)
            else:
                tail[index] = num
        return len(tail)



#乘积最大子数组
class Solution(object):
    def maxProduct(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        current_max = current_min = answer = nums[0]

        for num in nums[1:]:
            if num < 0:
                current_min, current_max = current_max, current_min

            current_min = min(num, current_min * num)
            current_max = max(num, current_max * num)
            answer = max(answer, current_max)
        return answer

#分割等和子集
class Solution(object):
    def canPartition(self, nums):
        """
        :type nums: List[int]
        :rtype: bool
        """
        total = sum(nums)

        if total % 2 == 1:
            return False
        target = total // 2

        probability = {0}

        for num in nums:
            probability |= {
                value + num
                for value in probability
                if value <= total
            }
        if target in probability:
            return True
        return False
        
# 动态规划