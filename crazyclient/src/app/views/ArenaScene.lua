local ArenaScene = class('ArenaScene', cc.load('mvc').ViewBase)

ArenaScene.RESOURCE_FILENAME = 'ArenaScene.csb'

require('json')

local POS_SCALE = 5

function ArenaScene:onCreate()
    self.cars = {}
    self.drawings = {}
    self.stageNode = self.resourceNode_:getChildByTag(19)
    self:createKeyboardHandler()
    self:bindJoin()
    self:resetStageDraw()
end

function ArenaScene:resetStageDraw()
    for k, v in pairs(self.drawings) do
        v:removeSelf()
    end
    self.drawings = {}

    local fu = cc.FileUtils:getInstance()
    local stageStr = fu:getStringFromFile('test-stage.json')
    local stageData = json.decode(stageStr, 1)

    for k, v in ipairs(stageData.stageObjects) do
        print(v.type)
        local color
        if v.type == 'start' then
            color = { r = 20, g = 10, b = 200}
        elseif v.type == 'finish' then
            color = { r = 0, g = 230, b = 10 }
        else
            color = { r = 190, g = 20, b = 20 }
        end
        local d = display.newLayer(color, { width = v.width / POS_SCALE, height = v.height / POS_SCALE })
            :move(display.cx + (v.x - v.width / 2) / POS_SCALE, display.cy + (v.y - v.height / 2) / POS_SCALE)
            :addTo(self.stageNode)

        self.drawings[d] = d
    end

    local bg = self.resourceNode_:getChildByTag(11)
    bg:setScale(1 / POS_SCALE, 1 / POS_SCALE)
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
                    self:message('INFO - joined id ' .. resj.car.id .. ' token ' .. resj.token)
                    self.token = resj.token
                    self.id = tostring(resj.car.id)
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
    print(msg)
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

        local car = self.cars[k]

        local x = v[1]
        local y = v[2]
        local a = v[3] -- 차체의 각도 (라디안)
        local ha = v[4] -- 핸들의 각도 (라디안))
        local th = v[5] -- 액셀 밟은 정도 (-100 ~ 100) 음수면 후진 액셀

        car:move(cc.p(display.cx + x/POS_SCALE,
            display.cy + y/POS_SCALE))
        car:setRotation(a / math.pi * 180)
        car:setScale(1.0/POS_SCALE, 1.0/POS_SCALE)
        if k == self.id then
            self:onPlayerHandleState(ha)
            self:onPlayerAccelState(th)

            if not car.label then
                car.label = cc.Label:createWithSystemFont('Player', 'Arial', 30)
                    :addTo(car)
            end
        end
    end

    self:scaleBg()

    self:queryFullState()
end

function ArenaScene:scaleBg()
    local bg = self.resourceNode_:getChildByTag(11)
    bg:setScale(1.0/POS_SCALE, 1.0/POS_SCALE)
end

function ArenaScene:onPlayerHandleState(handleRad)
    local handle = self.resourceNode_:getChildByTag(17)
    handle:setRotation(handleRad / math.pi * 180)
end

function ArenaScene:onPlayerAccelState(throttle)
    local th = self.resourceNode_:getChildByTag(14)
    th:setRotation(math.abs(throttle) / 100 * 40)
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
            self:throttleDelta(10)
        elseif keyCode == cc.KeyCode.KEY_DOWN_ARROW then
            self:throttleDelta(-10)
        elseif keyCode == cc.KeyCode.KEY_LEFT_ARROW then
            self:handleDelta(-math.pi / 256)
        elseif keyCode == cc.KeyCode.KEY_RIGHT_ARROW then
            self:handleDelta(math.pi / 256)
        elseif keyCode == cc.KeyCode.KEY_B then
            self:brake()
        elseif keyCode == cc.KeyCode.KEY_1 then
            POS_SCALE = 1
            self:resetStageDraw()
        elseif keyCode == cc.KeyCode.KEY_2 then
            POS_SCALE = 2
            self:resetStageDraw()
        elseif keyCode == cc.KeyCode.KEY_3 then
            POS_SCALE = 3
            self:resetStageDraw()
        elseif keyCode == cc.KeyCode.KEY_4 then
            POS_SCALE = 4
            self:resetStageDraw()
        elseif keyCode == cc.KeyCode.KEY_5 then
            POS_SCALE = 5
            self:resetStageDraw()
        end
    end

    local listener = cc.EventListenerKeyboard:create()
    listener:registerScriptHandler(onKeyReleased, cc.Handler.EVENT_KEYBOARD_RELEASED)

    local eventDispatcher = self:getEventDispatcher()
    eventDispatcher:addEventListenerWithSceneGraphPriority(listener, self)
end

return ArenaScene
