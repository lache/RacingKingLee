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
                local qs = string.format('/join/%s/red/normal', username)
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
    --print(res)
    local fs = json.decode(res, 1)
    for k, v in pairs(fs) do
        --print(k,v)
        if not self.cars[k] then
            self:createCar(k)
        end

        local params = split(v, ',')
        self.cars[k]:move(cc.p(display.cx + params[1]/POS_SCALE,
            display.cy + params[2]/POS_SCALE))
        self.cars[k]:setRotation(0)
    end

    self:queryFullState()
end

function ArenaScene:createCar(k)
    local s = cc.Sprite:create('car-top.png'):addTo(self)
    self.cars[k] = s
end

function ArenaScene:request(url, cb)
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
            print("[ERROR] xhr.readyState is:", xhr.readyState, "xhr.status is: ",xhr.status,fullUrl)
        end
    end

    xhr:registerScriptHandler(onReadyStateChange)
    xhr:send()
end

function ArenaScene:throttleDelta(d)
    if not self.token then self:message('ERROR - join first') end

    self:request(string.format('/accel/%s/%d', self.token, d), function (res)
        print(res)
    end)
end

function ArenaScene:handleDelta(d)
    if not self.token then self:message('ERROR - join first') end

    local nextDelta

    self:request(string.format('/handle/%s/%d', self.token, d), function (res)
        print(res)
    end)
end

function ArenaScene:brake()
    if not self.token then self:message('ERROR - join first') end

    self:request(string.format('/brake/%s', self.token), function (res)
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
            self:throttleDelta(10)
        elseif keyCode == cc.KeyCode.KEY_DOWN_ARROW then
            self:throttleDelta(-10)
        elseif keyCode == cc.KeyCode.KEY_LEFT_ARROW then
            self:handleDelta(-math.pi / 32)
        elseif keyCode == cc.KeyCode.KEY_RIGHT_ARROW then
            self:handleDelta(math.pi / 32)
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
