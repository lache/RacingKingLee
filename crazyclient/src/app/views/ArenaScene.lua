local ArenaScene = class('ArenaScene', cc.load('mvc').ViewBase)

ArenaScene.RESOURCE_FILENAME = 'ArenaScene.csb'

require('json')

local POS_SCALE = 1

function ArenaScene:onCreate()
    self.cars = {}
    self:createKeyboardHandler()
    self:bindJoin()
end

function ArenaScene:bindJoin()
    local plJoin = self.resourceNode_:getChildByTag(7)
    local btnJoin = plJoin:getChildByTag(5)
    btnJoin:addTouchEventListener(function(sender, eventType)
        if eventType == ccui.TouchEventType.ended then
            local tfUsername = plJoin:getChildByTag(4)
            local username = tfUsername:getString()
            if string.len(username) > 0 then
                plJoin:hide()
                self:message('INFO - wait...')
                local qs = string.format('/join?name=%s&color=red&type=normal', username)
                self:request(qs, function (res)
                    local resj = json.decode(res, 1)
                    self:message('INFO - joined ' .. resj.token)
                    self.token = resj.token

                    self:queryFullState()
                end)
            else
                self:message('ERROR - enter username')
            end
        end
    end)
end

function ArenaScene:queryFullState()
    self:request('/car_pos', function (res)
        self:onFullState(res)
    end, function (res)
        self:queryFullState() -- 어떤 이유에서라도 실패했다면 재시도한다.
    end)
end

function ArenaScene:message(msg)
    cc.Label:createWithSystemFont(msg, 'Arial', 30)
        :align(display.CENTER, cc.p(display.cx, display.cy))
        :addTo(self)
        :runAction(cc.Sequence:create(
            cc.DelayTime:create(0.1),
            cc.MoveTo:create(0.6, cc.p(display.cx,display.cy + 30)),
            cc.RemoveSelf:create()
        ))
end

local function split(inputstr, sep)
    if sep == nil then
        sep = "%s"
    end
    local t={}
    local i=1
    for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
        t[i] = str
        i = i + 1
    end
    return t
end

function ArenaScene:onFullState(res)
    --print('onFullState', res)
    local fs = json.decode(res, 1)
    for k, v in pairs(fs) do
        --print(k,v)
        if not self.cars[k] then
            self:createCar(k)
        end

        self.cars[k]:move(cc.p(display.cx + v[1]/POS_SCALE,
            display.cy + v[2]/POS_SCALE))
        self.cars[k]:setRotation(v[3] / math.pi * 180)
    end

    self:queryFullState()
end

function ArenaScene:createCar(k)
    local s = cc.Sprite:create('car-top.png'):addTo(self)
    self.cars[k] = s
end

function ArenaScene:request(url, cb, cberr)
    local xhr = cc.XMLHttpRequest:new()
    xhr.responseType = cc.XMLHTTPREQUEST_RESPONSE_STRING
    local fullUrl = "http://cosmosworld.cafe24.com:9999" .. url
    xhr:open("GET", fullUrl)
    --xhr:open("GET", "http://localhost:9999" .. url)

    local function onReadyStateChange()
        if xhr.readyState == 4 and (xhr.status >= 200 and xhr.status < 207) then
            --local statusString = "Http Status Code:"..xhr.statusText
            --print(xhr.response)
            if cb then
                cb(xhr.response)
            else
                print(xhr.response)
            end
        else
            if cberr then
                cberr()
            else
                print("[ERROR] xhr.readyState is:", xhr.readyState, "xhr.status is: ",xhr.status,fullUrl)
            end
        end
    end

    xhr:registerScriptHandler(onReadyStateChange)
    xhr:send()
end

function ArenaScene:throttleDelta(d)
    if not self.token then self:message('ERROR - join first') end

    self:request(string.format('/accel?token=%s&accel=%d', self.token, d), function (res)
        print(res)
    end)
end

function ArenaScene:handleDelta(d)
    if not self.token then self:message('ERROR - join first') end

    local nextDelta

    self:request(string.format('/handle?token=%s&angle=%f', self.token, d), function (res)
        print(res)
    end)
end

function ArenaScene:brake()
    if not self.token then self:message('ERROR - join first') end

    self:request(string.format('/brake?token=%s', self.token), function (res)
        print(res)
    end)
end

function ArenaScene:createKeyboardHandler()

    local function onKeyReleased(keyCode, event)
        if keyCode == cc.KeyCode.KEY_BACK then
            os.exit(0)
        elseif keyCode == cc.KeyCode.KEY_MENU then
        elseif keyCode == cc.KeyCode.KEY_S then
        elseif keyCode == cc.KeyCode.KEY_UP_ARROW then
            self:throttleDelta(50)
        elseif keyCode == cc.KeyCode.KEY_DOWN_ARROW then
            self:throttleDelta(-50)
        elseif keyCode == cc.KeyCode.KEY_LEFT_ARROW then
            self:handleDelta(-math.pi / 256)
        elseif keyCode == cc.KeyCode.KEY_RIGHT_ARROW then
            self:handleDelta(math.pi / 256)
        elseif keyCode == cc.KeyCode.KEY_B then
            self:brake()
        end
    end

    local listener = cc.EventListenerKeyboard:create()
    listener:registerScriptHandler(onKeyReleased, cc.Handler.EVENT_KEYBOARD_RELEASED)

    local eventDispatcher = self:getEventDispatcher()
    eventDispatcher:addEventListenerWithSceneGraphPriority(listener, self)
end

return ArenaScene
