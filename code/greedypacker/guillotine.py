#!/usr/bin/env python

import operator
import typing
import bisect
from typing import List, Tuple
from functools import reduce
from collections import namedtuple
from sortedcontainers import SortedListWithKey # type: ignore
from .item import Item


class FreeRectangle(typing.NamedTuple('FreeRectangle', [('width', int), ('height', int), ('x', int), ('y', int)])):
    __slots__ = ()
    @property
    def area(self):
        return self.width*self.height
"""
FreeRectangle类用于表示一个矩形，其中包含宽度、高度、左上角x坐标和左上角y坐标。typing.NamedTuple是一个帮助类，用于创建具有名称的元组类型。

__slots__属性用于限制实例的属性，使其只能添加或删除指定的属性。在这种情况下，__slots__设置为空，表示实例可以具有任意属性。

@property装饰器用于将方法转换为属性。在这种情况下，area方法被转换为属性，以便可以轻松地访问矩形的面积。

area方法返回矩形的宽度乘以高度，即矩形的面积。
"""

class Guillotine:
    def __init__(self, x: int = 8,
                 y: int = 4,
                 rotation: bool = True,
                 heuristic: str = 'best_area_fit',
                 rectangle_merge: bool = True,
                 split_heuristic: str = 'default') -> None:
        self.x = x
        self.y = y
        self.area = self.x * self.y
        self.free_area = self.x * self.y
        self.rMerge = rectangle_merge
        self.split_heuristic = split_heuristic

        if heuristic == 'best_area':
            self._score = scoreBAF
        elif heuristic == 'best_shortside':
            self._score = scoreBSSF
        elif heuristic == 'best_longside':
            self._score = scoreBLSF
        elif heuristic == 'worst_area':
            self._score = scoreWAF
        elif heuristic == 'worst_shortside':
            self._score = scoreWSSF
        elif heuristic == 'worst_longside':
            self._score = scoreWLSF
        else:
            raise ValueError('No such heuristic!')

        if x == 0 or y == 0:
            #self.freerects = [] # type: List[FreeRectangle]
            self.freerects = SortedListWithKey(iterable=None, key=lambda x: x.area)
        else:
            self.freerects = SortedListWithKey([FreeRectangle(self.x, self.y, 0, 0)], key=lambda x: x.area)
        self.items = [] # type: List[Item]
        self.rotation = rotation


    def __repr__(self) -> str:
        return "Guillotine(%r)" % (self.items)
    """
    __repr__ 方法是一个特殊方法，用于返回一个对象的字符串表示，
    通常用于调试和打印对象。
    在这个实现中，__repr__ 方法返回一个字符串，
    表示 Guillotine 类的实例（self）的 items 属性。
    """

    @staticmethod
    def _item_fits_rect(item: Item,
                       rect: FreeRectangle,
                       rotation: bool=False) -> bool:
        if (not rotation and
            item.width <= rect.width and 
            item.height <= rect.height):
            return True
        if (rotation and 
            item.height <= rect.width and 
            item.width <= rect.height):
            return True
        return False
    """
    _item_fits_rect 是一个静态方法（staticmethod），
    用于判断一个物品（item）是否可以放入一个矩形区域（rect）。
    这个方法有两个参数：item 表示要放入矩形的物品，rect 表示矩形区域。
    rotation 参数表示是否允许物品旋转，默认为 False。
    """

    @staticmethod
    def _split_along_axis(freeRect: FreeRectangle,
                          item: Item, split: bool) -> List[FreeRectangle]:
        top_x = freeRect.x
        top_y = freeRect.y + item.height
        top_h = freeRect.height - item.height

        right_x = freeRect.x + item.width
        right_y = freeRect.y
        right_w = freeRect.width - item.width

        # horizontal split
        if split:
            top_w = freeRect.width
            right_h = item.height
        # vertical split
        else:
            top_w = item.width
            right_h = freeRect.height

        result = []

        if right_w > 0 and right_h > 0:
            right_rect = FreeRectangle(right_w, right_h, right_x, right_y)
            result.append(right_rect)

        if top_w > 0 and top_h > 0:
            top_rect = FreeRectangle(top_w, top_h, top_x, top_y)
            result.append(top_rect)
        return result
    """
    这段代码定义了一个名为 `_split_along_axis` 的静态方法，
    它主要用于将一个给定的空闲矩形（`freeRect`）根据给定的项目（`item`）沿给定的轴（`split`）进行分割。这个方法主要用于二维空间中的矩形分割。

    具体来说，这个方法首先计算出两个新的矩形（`top_rect` 和 `right_rect`），它们是按照给定的项目（`item`）的尺寸和位置从给定的空闲矩形（`freeRect`）中分割出来的。
    然后，这个方法检查这两个新矩形是否满足条件（即它们的宽度和高度都大于 0），如果满足条件，则将它们添加到结果列表（`result`）中。最后，返回结果列表。

    这个方法主要用于二维空间中的矩形分割，特别是用于计算布局算法中的空闲矩形分割。
    在计算布局算法中，空闲矩形通常表示为一系列的矩形，这些矩形可以用来放置项目。
    通过使用这个方法，可以有效地将一个空闲矩形分割成两个更小的矩形，从而为项目找到一个合适的放置位置。

    需要注意的是，这个方法是一个静态方法，它不需要实例化类就可以直接调用。
    在调用这个方法时，需要传入三个参数：一个空闲矩形（`freeRect`），一个项目（`item`）以及一个表示分割轴的布尔值（`split`）。
    其中，`split` 为 `True` 时表示沿水平轴分割，为 `False` 时表示沿垂直轴分割。

    """

    def _split_free_rect(self, item: Item,
                         freeRect: FreeRectangle) -> List[FreeRectangle]:
        """
        Determines the split axis based upon the split heuristic then calls
        _split_along_axis  with the appropriate axis to return a List[FreeRectangle].
        """

        # Leftover lengths
        w = freeRect.width - item.width
        h = freeRect.height - item.height

        if self.split_heuristic == 'SplitShorterLeftoverAxis': split = (w <= h)
        elif self.split_heuristic == 'SplitLongerLeftoverAxis': split = (w > h)
        elif self.split_heuristic == 'SplitMinimizeArea': split = (item.width * h > w * item.height)
        elif self.split_heuristic == 'SplitMaximizeArea': split = (item.width * h <= w * item.height)
        elif self.split_heuristic == 'SplitShorterAxis': split = (freeRect.width <= freeRect.height)
        elif self.split_heuristic == 'SplitLongerAxis': split = (freeRect.width > freeRect.height)
        else: split = True


        return self._split_along_axis(freeRect, item, split)


    def _add_item(self, item: Item, x: int, y: int, rotate: bool = False) -> None:
        """ Helper method for adding items to the bin """
        if rotate:
            item.rotate()
        item.x, item.y = x, y
        self.items.append(item)
        self.free_area -= item.area

    """
    _add_item方法是一个辅助方法，用于将一个矩形添加到Bin对象中。
    它接受一个Item对象作为参数，表示要添加的矩形，
    以及矩形在空间中的坐标(x, y)和旋转标志rotate。
    如果rotate为True，则矩形将被旋转。
    """

    def rectangle_merge(self) -> None:
        """
        Rectangle Merge optimization
        Finds pairs of free rectangles and merges them if they are mergable.
        """
        for freerect in self.freerects:
            widths_func = lambda r: (r.width == freerect.width and
                                     r.x == freerect.x and r != freerect)
            matching_widths = list(filter(widths_func, self.freerects))
            heights_func = lambda r: (r.height == freerect.height and
                                      r.y == freerect.y and r != freerect)
            matching_heights = list(filter(heights_func, self.freerects))
            if matching_widths:
                widths_adjacent = list(filter(lambda r: r.y == freerect.y + freerect.height, matching_widths)) # type: List[FreeRectangle]

                if widths_adjacent:
                    match_rect = widths_adjacent[0]
                    merged_rect = FreeRectangle(freerect.width,
                                                freerect.height+match_rect.height,
                                                freerect.x,
                                                freerect.y)
                    self.freerects.remove(freerect)
                    self.freerects.remove(match_rect)
                    self.freerects.add(merged_rect)

            if matching_heights:
                heights_adjacent = list(filter(lambda r: r.x == freerect.x + freerect.width, matching_heights))
                if heights_adjacent:
                    match_rect = heights_adjacent[0]
                    merged_rect = FreeRectangle(freerect.width+match_rect.width,
                                                freerect.height,
                                                freerect.x,
                                                freerect.y)
                    self.freerects.remove(freerect)
                    self.freerects.remove(match_rect)
                    self.freerects.add(merged_rect)
            """
            rectangle_merge函数的输入参数为一个Bin对象，
            它表示一个二维空间，其中包含一些矩形。
            Bin对象有一个items属性，表示已经放置在空间中的矩形；

            还有一个freerects属性，表示尚未被占用的矩形。

            rectangle_merge函数首先遍历freerects中的每个矩形，
            检查是否有其他矩形与当前矩形在宽度和高度上匹配。如果找到匹配的矩形，
            那么就尝试将它们合并成一个更大的矩形。

            具体来说，它会检查当前矩形和匹配矩形是否相邻，
            如果相邻，那么就合并它们。
            合并后的矩形将替换原来的两个矩形。
            """

    def _find_best_score(self, item: Item):
        rects = []
        for rect in self.freerects:
            if self._item_fits_rect(item, rect):
                rects.append((self._score(rect, item), rect, False))
            if self.rotation and self._item_fits_rect(item, rect, rotation=True):
                rects.append((self._score(rect, item), rect, True))
        try:
            _score, rect, rot = min(rects, key=lambda x: x[0])
            return _score, rect, rot
        except ValueError:
            return None, None, False

    """这段代码是用于寻找一个物品（item）在给定矩形列表（freerects）中的最佳得分（_score）和最佳矩形（rect）以及是否旋转（rot）。

    具体实现原理如下：

    1. 遍历给定的矩形列表（freerects），对于每个矩形（rect），检查物品（item）是否可以放入该矩形中。如果可以，计算物品（item）在该矩形中的得分（_score），并将得分和矩形以及是否旋转（rot）添加到rects列表中。

    2. 如果物品（item）可以旋转，再次检查物品（item）是否可以放入该矩形中，如果可以，计算物品（item）在该矩形中的得分（_score），并将得分和矩形以及是否旋转（rot）添加到rects列表中。

    3. 对rects列表进行排序，选择得分最小的元素，作为最佳得分（_score），最佳矩形（rect）以及是否旋转（rot）。

    4. 如果rects列表为空，则返回None，None，False。


    注意事项：

    1. 物品（item）的尺寸必须小于等于矩形（rect）的尺寸。

    2. 如果物品（item）可以旋转，需要考虑旋转后的尺寸是否满足要求。

    3. _score函数用于计算物品（item）在给定矩形（rect）中的得分，具体实现可能因应用场景而有所不同。

    """

    def insert(self, item: Item, heuristic: str = 'best_area') -> bool:
        """
        Add items to the bin. Public Method.
        """
        _, best_rect, rotated = self._find_best_score(item)
        if best_rect:
            self._add_item(item, best_rect.x, best_rect.y, rotated)
            self.freerects.remove(best_rect)
            splits = self._split_free_rect(item, best_rect)
            for rect in splits:
                self.freerects.add(rect)
            if self.rMerge:
                self.rectangle_merge()
            return True
        return False
    """
    insert 函数是这个算法的公共方法，用于向当前的布局中添加一个新的矩形。
    函数的参数有两个：item 是要添加的矩形，heuristic 是用于选择最佳布局的启发式方法，默认为 'best_area'。

    函数首先使用 _find_best_score 函数找到可以容纳新矩形的最佳布局，然后使用 _add_item 函数将新矩形添加到布局中。
    接下来，从空闲区域中移除已使用的区域，并使用 _split_free_rect 函数将剩余的空闲区域分割成更小的区域。
    最后，如果启用了 rMerge 选项，则使用 rectangle_merge 函数进行矩形合并。
    """

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

"""
scoreBAF函数：Best Area Fit，最佳面积适应性。计算矩形面积减去物品面积的差值和矩形宽度和高度减去物品宽度和高度的差值中的较小值。

scoreBSSF函数：Best Shortside Fit，最佳短边适应性。计算矩形宽度和高度减去物品宽度和高度的差值中的较小值和矩形宽度和高度减去物品宽度和高度的差值中的较大值。

scoreBLSF函数：Best Longside Fit，最佳长边适应性。计算矩形宽度和高度减去物品宽度和高度的差值中的较大值和矩形宽度和高度减去物品宽度和高度的差值中的较小值。

scoreWAF函数：Worst Area Fit，最差面积适应性。计算0减去矩形面积减去物品面积的差值和0减去矩形宽度和高度减去物品宽度和高度的差值中的较小值。

scoreWSSF函数：Worst Shortside Fit，最差短边适应性。计算0减去矩形宽度和高度减去物品宽度和高度的差值中的较小值和0减去矩形宽度和高度减去物品宽度和高度的差值中的较大值。

scoreWLSF函数：Worst Longside Fit，最差长边适应性。计算0减去矩形宽度和高度减去物品宽度和高度的差值中的较大值和0减去矩形宽度和高度减去物品宽度和高度的差值中的较小值。
"""

def scoreBAF(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Best Area Fit """
    return rect.area-item.area, min(rect.width-item.width, rect.height-item.height)
        

def scoreBSSF(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Best Shortside Fit """
    return min(rect.width-item.width, rect.height-item.height), max(rect.width-item.width, rect.height-item.height)


def scoreBLSF(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Best Longside Fit """
    return max(rect.width-item.width, rect.height-item.height), min(rect.width-item.width, rect.height-item.height)


def scoreWAF(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Worst Area Fit """
    return (0 - (rect.area-item.area)), (0 - min(rect.width-item.width, rect.height-item.height))
        

def scoreWSSF(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Worst Shortside Fit """
    return (0 - min(rect.width-item.width, rect.height-item.height)), (0 - max(rect.width-item.width, rect.height-item.height))


def scoreWLSF(rect: FreeRectangle, item: Item) -> Tuple[int, int]:
    """ Worst Longside Fit """
    return (0 - max(rect.width-item.width, rect.height-item.height)), (0 - min(rect.width-item.width, rect.height-item.height))

"""
scoreBAF函数：Best Area Fit，最佳面积适应性。计算矩形面积减去物品面积的差值和矩形宽度和高度减去物品宽度和高度的差值中的较小值。

scoreBSSF函数：Best Shortside Fit，最佳短边适应性。计算矩形宽度和高度减去物品宽度和高度的差值中的较小值和矩形宽度和高度减去物品宽度和高度的差值中的较大值。

scoreBLSF函数：Best Longside Fit，最佳长边适应性。计算矩形宽度和高度减去物品宽度和高度的差值中的较大值和矩形宽度和高度减去物品宽度和高度的差值中的较小值。

scoreWAF函数：Worst Area Fit，最差面积适应性。计算0减去矩形面积减去物品面积的差值和0减去矩形宽度和高度减去物品宽度和高度的差值中的较小值。

scoreWSSF函数：Worst Shortside Fit，最差短边适应性。计算0减去矩形宽度和高度减去物品宽度和高度的差值中的较小值和0减去矩形宽度和高度减去物品宽度和高度的差值中的较大值。

scoreWLSF函数：Worst Longside Fit，最差长边适应性。计算0减去矩形宽度和高度减去物品宽度和高度的差值中的较大值和0减去矩形宽度和高度减去物品宽度和高度的差值中的较小值。
"""
