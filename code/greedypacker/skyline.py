#!/usr/bin/env python

from typing import List, NamedTuple, Tuple
from sortedcontainers import SortedList

from . import guillotine
from .item import Item


SkylineSegment = NamedTuple('SkylineSegment', [('x', int),
                                               ('y', int),
                                               ('width', int)])


class Skyline:
    def __init__(self, width: int = 8,
                 height: int = 4,
                 rotation: bool = True,
                 wastemap: bool = True,
                 heuristic: str = 'bottom_left') -> None:
        self.width = width
        self.height = height
        self.filledheight = 0 #使用skyline填充后的近似最优高度
        starting_segment = SkylineSegment(0, 0, width)
        self.skyline = SortedList([starting_segment])
        self.items = [] # type: List[Item]
        self.area = self.width * self.height
        self.free_area = self.width * self.height
        self.rotation = rotation
        self.use_waste_map = wastemap
        if self.use_waste_map:
            self.wastemap = guillotine.Guillotine(0, 0, rotation=self.rotation, heuristic='best_area')

        self.heuristic = heuristic
        if heuristic == 'bottom_left':
            self._score = scoreBL
        elif heuristic == 'best_fit':
            self._score = scoreBF
        else:
            raise ValueError('No such heuristic!')


    def __repr__(self) -> str:
        return "Skyline(%r)" % (self.items)

    """
    这段代码定义了一个名为 `_clip_segment` 的函数，它接受两个参数：`segment` 和 `item`，分别表示天际线段和项目。函数的目的是将天际线段按照项目进行裁剪，返回裁剪后的天际线段列表。

    具体实现过程如下：

    1. 首先，判断 `segment` 是否在 `item` 的下方，如果不在，则直接返回 `[segment]`。
    2. 如果 `segment` 完全在 `item` 的下方，则返回空列表。
    3. 如果 `segment` 部分在 `item` 的下方（左边），则创建一个新的天际线段 `new_segment`，其宽度为 `itemx-segx`，高度与 `segment` 相同，然后返回 `[new_segment]`。
    4. 如果 `segment` 部分在 `item` 的下方（右边），则创建一个新的天际线段 `new_segment`，其宽度为 `(seg_end_x)-item_end_x`，高度与 `segment` 相同，然后返回 `[new_segment]`。
    5. 如果 `segment` 在 `item` 的下方两边都部分覆盖，则分别创建两个新的天际线段 `new_segment_left` 和 `new_segment_right`，分别表示左边和右边的部分，然后返回 `[new_segment_left, new_segment_right]`。
    6. 如果以上情况都不满足，则返回空列表。

    需要注意的是，这个函数是私有的，只能在类 `Skyline` 的内部使用。同时，`SkylineSegment` 和 `Item` 类没有给出定义，所以无法完全理解这个函数的用途。
    """
    @staticmethod
    def _clip_segment(segment: SkylineSegment, item: Item) -> List[SkylineSegment]:
        """
        Clip out the length of segment adjacent to the item. 
        Return the rest.
        """
        # Segment not under new item
        itemx = item.x
        item_end_x = itemx + item.width
        segx = segment.x
        seg_end_x = segx + segment.width
        if segx > item_end_x or segx+segment.width<itemx:
            return [segment]
        # Segment fully under new item
        elif segx >= itemx and seg_end_x <= item_end_x:
            return []
        # Segment partialy under new item (to the left)
        elif segx < itemx and seg_end_x <= item_end_x:
            new_segment = SkylineSegment(segx, segment.y, itemx-segx)        
            return [new_segment]
        # Segment partially under new item (to the right)
        elif segx >= itemx and segx+segment.width > item_end_x:
            new_segment = SkylineSegment(item_end_x,
                                         segment.y,
                                         (seg_end_x)-item_end_x)
            return [new_segment]
        # Segment wider then item in both directions
        elif segx < itemx and segx+segment.width > item_end_x:
            new_segment_left = SkylineSegment(segx,
                                              segment.y,
                                              itemx-segx)
            new_segment_right = SkylineSegment(item_end_x,
                                               segment.y,
                                               (seg_end_x)-item_end_x)
            return [new_segment_left, new_segment_right]
        else:
            return []


    def _update_segment(self, segment: SkylineSegment, y:int, item: Item) -> List[SkylineSegment]:
        """
        Clips the line segment under the new item and returns
        an updated skyline segment list.
        """
        if self.use_waste_map:
            seg_i = self.skyline.index(segment)
            self._add_to_wastemap(seg_i, item, y)

        new_segments = SortedList([])
        for seg in self.skyline:
            new_segments.update(self._clip_segment(seg, item))

        # Create new segment if room above item
        if item.height + item.y < self.height:
            new_seg_y = item.y + item.height
            new_seg = SkylineSegment(segment.x, new_seg_y, item.width)
            new_segments.add(new_seg)
       
        return new_segments


    def _merge_segments(self) -> None:
        """
        Merge any adjacent SkylineSegments
        """
        new_segments = SortedList([self.skyline[0]])
        for seg in self.skyline[1:]:
            last = new_segments[-1]
            if seg.y == last.y and seg.x == last.x+last.width:
                new_last = SkylineSegment(last.x, last.y, 
                                          (seg.x+seg.width)-last.x)
                new_segments.remove(last)
                new_segments.add(new_last)
                continue
            new_segments.add(seg)

        self.skyline = new_segments
        """
        遍历输入的天际线列表（self.skyline），将第一个元素作为初始值，存入新的列表（new_segments）中。
        对于列表中的其他元素，分别与new_segments中的最后一个元素进行比较。
        如果当前元素的y坐标和new_segments中最后一个元素的y坐标相同，且当前元素的x坐标等于new_segments中最后一个元素的x坐标加宽度，说明这两个元素是相邻的线段，可以合并。将new_segments中最后一个元素从列表中移除，并添加一个新的SkylineSegment对象（new_last），表示合并后的线段。
        如果当前元素不能与new_segments中的最后一个元素合并，将当前元素添加到new_segments中。
        遍历结束后，将new_segments赋值给self.skyline，作为新的天际线列表。
        """


    def _check_fit(self, item_width: int,
                  item_height: int,
                  sky_index: int) -> Tuple[bool, int]:
        """
        Returns true if the item will fit above the skyline
        segment sky_index. Also works if the item is wider 
        then the segment.
        """
        i = sky_index#对浪费地图进行矩形合并（rectangle_merge）
        x = self.skyline[i].x
        y = self.skyline[i].y
        width = item_width

        #保证物品的宽度高度加上x坐标大于裁剪器的宽度
        if x + item_width > self.width:
            return (False, None)
        if y + item_height > self.height:
            return (False, None)

        while width > 0:#当物品的宽度大于0时，遍历天际线段。如果y坐标大于当前天际线段的最上端坐标，返回
            y = max(y, self.skyline[i].y)
            if (y + item_height > self.height):
                return (False, None)#如果物品的宽度大于当前天际线段的最右端坐标与x坐标的差值，返回（False，None）
            width -= self.skyline[i].width
            i += 1
            if width > 0 and i == len(self.skyline):
                return (False, None)#如果物品的宽度大于当前天际线段的最右端坐标与x坐标的差值，返回（False，None）
        #如果物品能够适应天际线段，返回（True，y）
        return (True, y)


    def _add_to_wastemap(self, seg_index: int,
                        item: Item, 
                        y: int) -> bool:
        """
        Identify wasted space when inserting
        item above segment. Add this space as 
        FreeRectangles into the wastemap
        """
        # New node edges
        item_left = self.skyline[seg_index].x
        item_right = item_left + item.width
        for seg in self.skyline[seg_index:]: 
            if seg.x >= item_right or seg.x + seg.width <= item_left: 
                break#遍历天际线（skyline）中的所有节点（seg），如果节点的x坐标在物品右侧或物品左侧与节点右侧之间，则跳出循环。
            left_side = seg.x
            right_side = min(item_right, seg.x + seg.width)#获取当前物品的左侧边界（item_left）和右侧边界（item_right）。

            w_width = right_side - left_side        
            w_height = y - seg.y
            w_x = left_side
            w_y = seg.y             #对于每个节点，计算浪费空间的大小（w_width和w_height）和位置（w_x和w_y）。
            if w_width > 0 and w_height > 0:
                waste_rect = guillotine.FreeRectangle(w_width,
                                                      w_height,
                                                      w_x,
                                                      w_y)
                self.wastemap.freerects.add(waste_rect)#如果浪费空间的大小大于0，则创建一个FreeRectangle对象（waste_rect），并将其添加到浪费地图的freerects集合中。
                self.wastemap.rectangle_merge()#对浪费地图进行矩形合并（rectangle_merge）



    def _find_best_score(self, item: Item) -> Tuple[int, SkylineSegment, int, bool]:#函数的输入参数是一个物品（Item）对象，表示要放置的矩形建筑物。函数返回一个元组，包含四个元素：物品的宽度、天际线段、物品的旋转状态和物品的放置位置。
        segs = []#函数首先创建一个空列表segs，用于存储可能的天际线段。
        for i, segment in enumerate(self.skyline):#然后遍历天际线列表，对于每个天际线段，检查物品是否可以放置在其中
            fits, y = self._check_fit(item.width, item.height, i)#如果可以放置，计算物品的得分，并将得分、天际线段和物品的放置位置添加到segs列表中
            if fits: 
                score = self._score(self.skyline, item, y, i)
                segs.append((score, segment, y, False))#如果物品可以旋转，同样检查物品是否可以放置在其中，并计算物品的得分
            if self.rotation:
                fits, y = self._check_fit(item.height, item.width, i)
                if fits:
                    score = self._score(self.skyline, item, y, i, rotation=True)
                    segs.append((score, segment, y, True))
        try:
            _score, seg, y, rot = min(segs, key=lambda x: x[0])
            return _score, seg, rot, y#尝试从segs列表中找到得分最小的元素，并返回其对应的物品宽度、天际线段、物品的旋转状态和物品的放置位置。如果segs列表为空，则返回None。
        except ValueError:
            return None, None, None, False
        


    def insert(self, item: Item,
               heuristic: str = 'bottom_left') -> bool:#它主要用于将一个名为item的Item对象插入到一个名为wastemap的Wastemap对象中。函数的第二个参数heuristic是一个字符串，表示插入算法的策略，默认为'bottom_left'
        """
        Wrapper for insertion heuristics
        """
        if self.wastemap:
            res = self.wastemap.insert(item, heuristic='best_area')
            if res:#函数首先检查wastemap是否为空，如果非空，则使用wastemap.insert()方法尝试插入item
                self.items.append(item)
                self.free_area -= item.width * item.height
                return True
        #如果wastemap为空，或者插入失败，则使用_find_best_score()方法找到一个最佳插入位置。
        #这个方法会返回一个元组，包含最佳插入位置的得分、最佳插入位置的Segment对象、是否需要旋转item以及最佳插入位置的y坐标。
        _, best_seg, rotation, best_y = self._find_best_score(item)#如果插入成功，将item添加到items列表中，并更新free_area。
        if best_y+item.height>self.filledheight:
            self.filledheight=best_y+item.height
        #这个方法会返回一个元组，包含最佳插入位置的得分、最佳插入位置的Segment对象
        #是否需要旋转item以及最佳插入位置的y坐标。
        
        if best_seg:
            if rotation:
                item.rotate()
            item.x, item.y = (best_seg.x, best_y)
            self.items.append(item)
            self.free_area -= item.width * item.height
            self.skyline = self._update_segment(best_seg, best_y, item)
            #是否需要旋转item以及最佳插入位置的y坐标。
            self._merge_segments()
            return True
        return False


    def bin_stats(self) -> dict:
        """
        Returns a dictionary with compiled stats on the bin tree
        """

        stats = {
            'width': self.x,
            'height': self.y,
            'area': self.area,
            'efficiency': (self.area - self.free_area) / self.area,
            'items': self.items,
            }

        return stats


def scoreBL(segs: List[SkylineSegment], item: Item, y: int, i: int, rotation=False) -> Tuple[int, int]:
    """ Bottom Left """
    seg = segs[i]
    if rotation:
        return item.width + y, seg.width
    return item.height + y, seg.width 


def calc_waste(segs: List[SkylineSegment],
               item: Item,
               y: int,
               i: int,
               rotation: bool = False) -> int:
    """
    Returns the total wasted area if item is
    inserted above segment
    """
    wasted_area = 0
    item_left = segs[i].x
    if not rotation:
        item_right = item_left + item.width
    else:
        item_right = item_left + item.height
    for seg in segs[i:]:
        if seg.x >= item_right or seg.x + seg.width <= item_left:
            break
        left_side = seg.x
        right_side = min(item_right, seg.x + seg.width)
        wasted_area += (right_side - left_side) * (y - seg.y)
    return wasted_area
    """
    这是一个Python函数，名为`calc_waste`，它主要用于计算在给定天际线 segments（天际线段）中插入一个物品（Item）时可能浪费的面积。这个函数可以计算出在给定天际线 segments 中插入一个物品时，如果物品不旋转，那么浪费的面积；如果物品旋转，那么浪费的面积。

    函数的参数包括：

    - `segs`：一个 List[SkylineSegment] 类型的参数，表示天际线 segments。
    - `item`：一个 Item 类型的参数，表示要插入的物品。
    - `y`：一个 int 类型的参数，表示天际线的高度。
    - `i`：一个 int 类型的参数，表示要插入物品的索引。
    - `rotation`：一个 bool 类型的参数，表示物品是否旋转。默认值为 False。

    函数的返回值是一个 int 类型的参数，表示浪费的面积。

    函数的实现原理如下：

    1. 初始化一个名为`wasted_area`的变量，用于存储浪费的面积。
    2. 获取物品的左边界`item_left`，如果不旋转，那么`item_left`等于物品的左边界；如果旋转，那么`item_left`等于物品的顶部边界。
    3. 遍历天际线 segments 中从索引`i`开始的部分，对于每个 segment：
    a. 如果 segment 的左边界大于等于物品的右边界，或者 segment 的右边界小于等于物品的左边界，那么跳出循环。
    b. 计算 segment 的左边界和物品的右边界之间的距离，以及 segment 的 y 坐标和天际线的高度之间的距离，然后将这两个距离相乘，得到浪费的面积。将这个面积加到`wasted_area`中。
    4. 返回`wasted_area`。

    这个函数可以用于计算在给定天际线 segments 中插入一个物品时可能浪费的面积，从而帮助优化物品的插入位置，以减少浪费。

    """

def scoreBF(segs: List[SkylineSegment],
            item: Item, 
            y: int,
            i: int,
            rotation=False) -> Tuple[int, int]:
    """ Best Fit """

    if rotation:
        return (calc_waste(segs, item, y, i, rotation=True), item.width + y)
    return (calc_waste(segs, item, y, i, rotation=False), item.height + y)
