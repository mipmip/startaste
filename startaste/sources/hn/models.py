from startaste.db import Doc


class HnStory(Doc):
    class Meta:
        table_name = "hn_story"


class HnComment(Doc):
    class Meta:
        table_name = "hn_comment"
