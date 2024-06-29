"""
2D Item class.
"""
class Item:
    """
    Items class for rectangles inserted into sheets
    """
    def __init__(self, width, height,
                 CornerPoint: tuple = (0, 0),
                 rotation: bool = True) -> None:
        self.width = width  # 物品的宽度                       
        self.height = height # 物品的高度
        # 物品的左上角坐标
        self.x = CornerPoint[0]
        self.y = CornerPoint[1]
        self.area = self.width * self.height# 物品的面积
        self.rotated = False# 物品是否旋转
        self.id = 0# 物品的ID


    def __repr__(self):
        return 'Item(width=%r, height=%r, x=%r, y=%r)' % (self.width, self.height, self.x, self.y)


    def rotate(self) -> None:
        self.width, self.height = self.height, self.width# 交换物品的宽度和高度
        self.rotated = False if self.rotated == True else True# 反转物品的旋转状态
