from app.conference.services.upload_zip import get_position


def test_get_position():
    assert 1 == get_position("1.jpg")
    assert not get_position("image.jpg")
    assert 1 == get_position("slide1.png", prefix="slide")
    assert 1 == get_position("Slide1.png", prefix="slide")
    assert 1 == get_position("1.png", prefix="slide")
